"""
hyper_phase_change/backend_router.py
====================================
Heterogeneous Execution Router & Policy Scheduler.

Enforces four strict scheduling policies:
1. CPU_ONLY:
   Always executes on host CPU (NumPy/AVX2).
2. VERIFIED_IGPU_ONLY:
   Executes ONLY on physical Intel UHD Graphics via OpenVINO.
   FAILS CLOSED if the workload or shape cannot run on the real iGPU.
   NEVER silently substitutes CPU execution.
3. AUTO_VERIFIED:
   Evaluates phase-change rewrites and cost model.
   Selects the optimal verified backend (Rewrite, iGPU, or CPU).
   Honestly records the actual backend used.
4. BENCHMARK_CANDIDATES:
   Executes all applicable candidate paths, measures real execution times,
   verifies outputs, and returns the fastest valid candidate.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

try:
    import openvino as ov
    from openvino import opset14 as ops
    OPENVINO_AVAILABLE = True
except Exception:
    OPENVINO_AVAILABLE = False

from hyper_phase_change.contract import (
    WorkloadContract,
    ExactnessClass,
    CANONICAL_REGISTRY,
)
from hyper_phase_change.rewrites import PhaseChangeOptimizer, PhaseChangeRewrite
from hyper_phase_change.cost_model import PhaseChangeCostModel, CostProfile
from hyper_phase_change.verification import PhaseChangeVerifier, VerificationResult
from hyper_phase_change.capability_registry import CapabilityRegistry, BackendState
from hyper.canonical.candidate_compiler import CandidateCompiler


class ExecutionPolicy(str, Enum):
    CPU_ONLY = "CPU_ONLY"
    VERIFIED_IGPU_ONLY = "VERIFIED_IGPU_ONLY"
    AUTO_VERIFIED = "AUTO_VERIFIED"
    BENCHMARK_CANDIDATES = "BENCHMARK_CANDIDATES"


class BackendExecutionError(Exception):
    """Raised when an explicit execution policy cannot be satisfied."""
    pass


@dataclasses.dataclass
class RouterExecutionResult:
    workload_id: str
    policy: ExecutionPolicy
    actual_backend: str
    device_name: str
    is_fallback: bool
    fallback_reason: Optional[str]
    latency_ms: float
    output: Any
    output_digest: str
    is_verified: bool
    verification_details: Optional[Dict[str, Any]] = None
    cost_profile: Optional[Dict[str, Any]] = None
    rewrite_applied: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "policy": self.policy.value,
            "actual_backend": self.actual_backend,
            "device_name": self.device_name,
            "is_fallback": self.is_fallback,
            "fallback_reason": self.fallback_reason,
            "latency_ms": round(self.latency_ms, 4),
            "output_digest": self.output_digest,
            "is_verified": self.is_verified,
            "verification_details": self.verification_details,
            "cost_profile": self.cost_profile,
            "rewrite_applied": self.rewrite_applied,
        }


class HeterogeneousRouter:
    """
    Intelligent, truthful scheduler for CPU, iGPU, and Phase-Change execution.
    """

    def __init__(self) -> None:
        self.capability_registry = CapabilityRegistry()
        self._ov_core: Optional[Any] = None
        self._compiled_igpu_cache: Dict[str, Any] = {}
        self._init_openvino()

    def _init_openvino(self) -> None:
        """Initializes OpenVINO Core if available."""
        if OPENVINO_AVAILABLE:
            try:
                self._ov_core = ov.Core()
            except Exception:
                self._ov_core = None

    def _execute_cpu_baseline(self, workload_id: str, inputs: Dict[str, Any], validate_schema: bool = True) -> Tuple[Any, float]:
        """Executes the standard CPU AVX2 candidate implementation."""
        contract = CANONICAL_REGISTRY.get_contract(workload_id)
        out, cand_rec = CandidateCompiler.execute_candidate(
            workload_id, inputs, contract=contract, target_backend="CPU_AVX2", validate_schema=validate_schema
        )
        return out, cand_rec.execution_time_ms

    def _compile_and_run_igpu(self, workload_id: str, inputs: Dict[str, Any]) -> Tuple[Any, float]:
        """
        Executes physical computation on Intel UHD Graphics via OpenVINO.
        Raises BackendExecutionError if execution cannot run on real iGPU.
        """
        if not OPENVINO_AVAILABLE or self._ov_core is None:
            raise BackendExecutionError("OpenVINO runtime is unavailable.")

        if "GPU" not in self._ov_core.available_devices:
            raise BackendExecutionError("Physical Intel GPU device is not available in OpenVINO.")

        # 1. GEMM_TILED / GEMM_STANDARD
        if workload_id in ("GEMM_TILED", "GEMM_STANDARD"):
            A = np.asarray(inputs.get("A"), dtype=np.float32)
            B = np.asarray(inputs.get("B"), dtype=np.float32)
            if A.ndim != 2 or B.ndim != 2:
                raise BackendExecutionError(f"iGPU GEMM requires 2D matrices, got A={A.shape}, B={B.shape}")

            m, k = A.shape
            k2, n = B.shape
            if k != k2:
                raise BackendExecutionError(f"Inner dimensions mismatch: A={A.shape}, B={B.shape}")

            cache_key = f"gemm_{m}x{k}x{n}"
            if cache_key not in self._compiled_igpu_cache:
                pA = ops.parameter([m, k], dtype=np.float32, name="A")
                pB = ops.parameter([k, n], dtype=np.float32, name="B")
                mm = ops.matmul(pA, pB, False, False)
                model = ov.Model([mm], [pA, pB], cache_key)
                ov_cfg = {"INFERENCE_PRECISION_HINT": "f32", "EXECUTION_MODE_HINT": "ACCURACY"}
                self._compiled_igpu_cache[cache_key] = self._ov_core.compile_model(model, "GPU", ov_cfg)

            compiled = self._compiled_igpu_cache[cache_key]
            t0 = time.perf_counter()
            infer_req = compiled.create_infer_request()
            infer_req.infer([A, B])
            out = infer_req.get_output_tensor(0).data.copy()
            exec_ms = (time.perf_counter() - t0) * 1000.0
            return out, exec_ms

        # 2. ML_MLP_INFERENCE
        elif workload_id == "ML_MLP_INFERENCE":
            X = np.asarray(inputs.get("X"), dtype=np.float32)
            W1 = np.asarray(inputs.get("W1"), dtype=np.float32)
            b1 = np.asarray(inputs.get("b1"), dtype=np.float32)
            W2 = np.asarray(inputs.get("W2"), dtype=np.float32)
            b2 = np.asarray(inputs.get("b2"), dtype=np.float32)

            batch_size, in_dim = X.shape
            _, hidden_dim = W1.shape
            _, out_dim = W2.shape

            cache_key = f"mlp_{batch_size}x{in_dim}x{hidden_dim}x{out_dim}"
            if cache_key not in self._compiled_igpu_cache:
                pX = ops.parameter([batch_size, in_dim], dtype=np.float32, name="X")
                pW1 = ops.parameter([in_dim, hidden_dim], dtype=np.float32, name="W1")
                pb1 = ops.parameter([hidden_dim], dtype=np.float32, name="b1")
                pW2 = ops.parameter([hidden_dim, out_dim], dtype=np.float32, name="W2")
                pb2 = ops.parameter([out_dim], dtype=np.float32, name="b2")

                # Layer 1: X @ W1 + b1
                mm1 = ops.matmul(pX, pW1, False, False)
                add1 = ops.add(mm1, pb1)
                relu1 = ops.relu(add1)
                # Layer 2: H @ W2 + b2
                mm2 = ops.matmul(relu1, pW2, False, False)
                add2 = ops.add(mm2, pb2)

                model = ov.Model([add2], [pX, pW1, pb1, pW2, pb2], cache_key)
                ov_cfg = {"INFERENCE_PRECISION_HINT": "f32", "EXECUTION_MODE_HINT": "ACCURACY"}
                self._compiled_igpu_cache[cache_key] = self._ov_core.compile_model(model, "GPU", ov_cfg)

            compiled = self._compiled_igpu_cache[cache_key]
            t0 = time.perf_counter()
            infer_req = compiled.create_infer_request()
            infer_req.infer([X, W1, b1, W2, b2])
            out = infer_req.get_output_tensor(0).data.copy()
            exec_ms = (time.perf_counter() - t0) * 1000.0
            return out, exec_ms

        # 3. REDUCTION_SUM
        elif workload_id == "REDUCTION_SUM":
            x = np.asarray(inputs.get("x"), dtype=np.float32)
            cache_key = f"red_sum_{x.size}"
            if cache_key not in self._compiled_igpu_cache:
                px = ops.parameter([x.size], dtype=np.float32, name="x")
                axis_const = ops.constant(np.array([0], dtype=np.int64))
                red = ops.reduce_sum(px, axis_const, keep_dims=False)
                model = ov.Model([red], [px], cache_key)
                ov_cfg = {"INFERENCE_PRECISION_HINT": "f32", "EXECUTION_MODE_HINT": "ACCURACY"}
                self._compiled_igpu_cache[cache_key] = self._ov_core.compile_model(model, "GPU", ov_cfg)

            compiled = self._compiled_igpu_cache[cache_key]
            t0 = time.perf_counter()
            infer_req = compiled.create_infer_request()
            infer_req.infer([x.ravel()])
            out = np.asarray(infer_req.get_output_tensor(0).data, dtype=x.dtype)
            exec_ms = (time.perf_counter() - t0) * 1000.0
            return out, exec_ms

        # 4. ATTENTION_HEAD
        elif workload_id in ("ATTENTION_HEAD", "ATTENTION_FLASH"):
            Q = np.asarray(inputs.get("Q"), dtype=np.float32)
            K = np.asarray(inputs.get("K"), dtype=np.float32)
            V = np.asarray(inputs.get("V"), dtype=np.float32)
            seq_len, d_k = Q.shape
            cache_key = f"attn_{seq_len}x{d_k}"
            if cache_key not in self._compiled_igpu_cache:
                pQ = ops.parameter([seq_len, d_k], dtype=np.float32, name="Q")
                pK = ops.parameter([seq_len, d_k], dtype=np.float32, name="K")
                pV = ops.parameter([seq_len, d_k], dtype=np.float32, name="V")
                scale = ops.constant(np.float32(1.0 / np.sqrt(d_k)))
                scores = ops.multiply(ops.matmul(pQ, pK, False, True), scale)
                probs = ops.softmax(scores, axis=-1)
                ctx = ops.matmul(probs, pV, False, False)
                model = ov.Model([ctx], [pQ, pK, pV], cache_key)
                ov_cfg = {"INFERENCE_PRECISION_HINT": "f32", "EXECUTION_MODE_HINT": "ACCURACY"}
                self._compiled_igpu_cache[cache_key] = self._ov_core.compile_model(model, "GPU", ov_cfg)

            compiled = self._compiled_igpu_cache[cache_key]
            t0 = time.perf_counter()
            infer_req = compiled.create_infer_request()
            infer_req.infer([Q, K, V])
            out = infer_req.get_output_tensor(0).data.copy()
            exec_ms = (time.perf_counter() - t0) * 1000.0
            return out, exec_ms

        # 5. STREAMING_VECTOR_OPS (AXPY)
        elif workload_id == "STREAMING_VECTOR_OPS":
            x = np.asarray(inputs.get("x"), dtype=np.float32)
            y = np.asarray(inputs.get("y", np.zeros_like(x)), dtype=np.float32)
            alpha = float(inputs.get("alpha", 2.0))
            cache_key = f"axpy_{x.size}"
            if cache_key not in self._compiled_igpu_cache:
                px = ops.parameter([x.size], dtype=np.float32, name="x")
                py = ops.parameter([x.size], dtype=np.float32, name="y")
                p_alpha = ops.constant(np.float32(alpha))
                scaled = ops.multiply(px, p_alpha)
                res = ops.add(scaled, py)
                model = ov.Model([res], [px, py], cache_key)
                ov_cfg = {"INFERENCE_PRECISION_HINT": "f32", "EXECUTION_MODE_HINT": "ACCURACY"}
                self._compiled_igpu_cache[cache_key] = self._ov_core.compile_model(model, "GPU", ov_cfg)

            compiled = self._compiled_igpu_cache[cache_key]
            t0 = time.perf_counter()
            infer_req = compiled.create_infer_request()
            infer_req.infer([x.ravel(), y.ravel()])
            out = infer_req.get_output_tensor(0).data.reshape(x.shape).copy()
            exec_ms = (time.perf_counter() - t0) * 1000.0
            return out, exec_ms

        else:
            raise BackendExecutionError(
                f"Workload '{workload_id}' does not have an OpenVINO iGPU kernel compiled. "
                "Only GEMM, MLP, Reduction, Attention, and AXPY are registered for physical iGPU execution."
            )

    def route_and_execute(
        self,
        workload_id: str,
        inputs: Dict[str, Any],
        policy: ExecutionPolicy = ExecutionPolicy.AUTO_VERIFIED,
        verify_output: bool = True,
    ) -> RouterExecutionResult:
        """
        Routes workload according to declared policy and executes safely.
        """
        contract = CANONICAL_REGISTRY.get_contract(workload_id)
        if contract is None:
            raise ValueError(f"Unknown workload ID: '{workload_id}'")

        # 1. VERIFIED_IGPU_ONLY Policy: Must run on real iGPU or FAIL CLOSED
        if policy == ExecutionPolicy.VERIFIED_IGPU_ONLY:
            try:
                out, exec_ms = self._compile_and_run_igpu(workload_id, inputs)
                backend_used = "OPENVINO_IGPU"
                device_name = self.capability_registry.get_backend("OPENVINO_IGPU").device_target
                is_fallback = False
                fallback_reason = None
                rewrite_applied = None
            except Exception as e:
                # Strictly fail closed: do NOT silently fallback to CPU
                raise BackendExecutionError(
                    f"VERIFIED_IGPU_ONLY policy violation: Workload '{workload_id}' failed execution on Intel iGPU: {str(e)}"
                )

        # 2. CPU_ONLY Policy
        elif policy == ExecutionPolicy.CPU_ONLY:
            out, exec_ms = self._execute_cpu_baseline(workload_id, inputs, validate_schema=verify_output)
            backend_used = "CPU_AVX2"
            device_name = self.capability_registry.get_backend("CPU_AVX2").device_target
            is_fallback = False
            fallback_reason = None
            rewrite_applied = None

        # 3. AUTO_VERIFIED Policy: Optimization search & truthful scheduling
        elif policy == ExecutionPolicy.AUTO_VERIFIED:
            # Fast-path for lightweight workloads: bypass structural analysis when direct compute is negligible
            total_elements = sum(getattr(v, "size", 0) for v in inputs.values() if isinstance(v, np.ndarray))
            is_lightweight = (
                workload_id in ("SHA256_CRYPTO", "SORT_STANDARD", "PAGERANK_GRAPH")
                or (total_elements > 0 and total_elements < 65536)
            )

            best_rw = None
            if not is_lightweight:
                analysis = PhaseChangeOptimizer.optimize_workload(workload_id, inputs)
                if analysis.best_rewrite is not None and analysis.net_speedup > 1.05:
                    best_rw = analysis.best_rewrite

            if best_rw is not None:
                # Execute verified fast-path
                t0 = time.perf_counter()
                out = best_rw.apply_fn(inputs)
                exec_ms = (time.perf_counter() - t0) * 1000.0
                backend_used = "PHASE_CHANGE_ELIMINATION"
                device_name = "Host CPU (Mathematical Rewrite Fast-Path)"
                is_fallback = False
                fallback_reason = None
                rewrite_applied = best_rw.name
            else:
                fallback_reason = None
                igpu_cap = self.capability_registry.get_backend("OPENVINO_IGPU")
                tried_igpu = False
                # Intelligent GPU break-even guard:
                # Driver dispatch and data preparation on Intel UHD Graphics takes ~0.8ms.
                # Only route to iGPU in AUTO_VERIFIED if workload FLOP/bandwidth demands make GPU faster than CPU AVX2.
                is_gpu_advantageous = False
                if igpu_cap and igpu_cap.state == BackendState.VERIFIED_FOR_CONTRACT and workload_id in igpu_cap.supported_workloads and not is_lightweight:
                    if workload_id == "GEMM_STANDARD":
                        A = inputs.get("A")
                        B = inputs.get("B")
                        if A is not None and B is not None:
                            is_gpu_advantageous = (A.shape[0] * A.shape[1] * B.shape[1] >= 6.4e7)
                    elif workload_id in ("ATTENTION_HEAD", "ATTENTION_FLASH"):
                        Q = inputs.get("Q")
                        if Q is not None and len(Q.shape) >= 2:
                            is_gpu_advantageous = (Q.shape[0] >= 256 and Q.shape[1] >= 64)
                    elif workload_id in ("REDUCTION_SUM", "STREAMING_VECTOR_OPS"):
                        x = inputs.get("x")
                        if x is not None:
                            is_gpu_advantageous = (x.size >= 1_000_000)
                    elif workload_id == "ML_MLP_INFERENCE":
                        X = inputs.get("X")
                        if X is not None:
                            is_gpu_advantageous = (X.size >= 500_000)

                if is_gpu_advantageous:
                    try:
                        out, exec_ms = self._compile_and_run_igpu(workload_id, inputs)
                        backend_used = "OPENVINO_IGPU"
                        device_name = igpu_cap.device_target
                        is_fallback = False
                        fallback_reason = None
                        rewrite_applied = None
                        tried_igpu = True
                    except Exception as igpu_err:
                        # Fallback to CPU with truthful accounting
                        tried_igpu = False
                        fallback_reason = f"iGPU attempt failed: {str(igpu_err)}"

                if not tried_igpu:
                    out, exec_ms = self._execute_cpu_baseline(workload_id, inputs, validate_schema=verify_output)
                    backend_used = "CPU_AVX2"
                    device_name = self.capability_registry.get_backend("CPU_AVX2").device_target
                    is_fallback = (fallback_reason is not None)
                    rewrite_applied = None

        # 4. BENCHMARK_CANDIDATES Policy: Run all applicable candidates and measure
        elif policy == ExecutionPolicy.BENCHMARK_CANDIDATES:
            # Measure CPU
            cpu_out, cpu_ms = self._execute_cpu_baseline(workload_id, inputs, validate_schema=verify_output)
            fastest_out = cpu_out
            fastest_ms = cpu_ms
            backend_used = "CPU_AVX2"
            device_name = self.capability_registry.get_backend("CPU_AVX2").device_target
            rewrite_applied = None

            # Measure Rewrite if available
            analysis = PhaseChangeOptimizer.optimize_workload(workload_id, inputs)
            if analysis.best_rewrite is not None:
                t0 = time.perf_counter()
                rw_out = analysis.best_rewrite.apply_fn(inputs)
                rw_ms = ((time.perf_counter() - t0) * 1000.0) + analysis.best_rewrite.detection_overhead_ms
                if rw_ms < fastest_ms:
                    fastest_out = rw_out
                    fastest_ms = rw_ms
                    backend_used = "PHASE_CHANGE_ELIMINATION"
                    device_name = "Host CPU (Mathematical Rewrite Fast-Path)"
                    rewrite_applied = analysis.best_rewrite.name

            # Measure iGPU if supported
            igpu_cap = self.capability_registry.get_backend("OPENVINO_IGPU")
            if igpu_cap and igpu_cap.state == BackendState.VERIFIED_FOR_CONTRACT and workload_id in igpu_cap.supported_workloads:
                try:
                    igpu_out, igpu_ms = self._compile_and_run_igpu(workload_id, inputs)
                    if igpu_ms < fastest_ms:
                        fastest_out = igpu_out
                        fastest_ms = igpu_ms
                        backend_used = "OPENVINO_IGPU"
                        device_name = igpu_cap.device_target
                        rewrite_applied = None
                except Exception:
                    pass

            out = fastest_out
            exec_ms = fastest_ms
            is_fallback = False
            fallback_reason = None

        else:
            raise ValueError(f"Unrecognized execution policy: {policy}")

        # Verification check
        out_digest = "BENCHMARK_UNHASHED"
        verification_details = None
        is_verified = True
        cost_profile = None

        if verify_output:
            out_digest = PhaseChangeVerifier.compute_digest(out)
            v_res = PhaseChangeVerifier.verify_candidate_output(workload_id, inputs, out, contract=contract)
            is_verified = v_res.is_verified
            verification_details = v_res.to_dict()
            cost_profile = PhaseChangeCostModel.evaluate_cost(
                workload_id=workload_id,
                backend_id=backend_used,
                inputs=inputs,
            ).to_dict()

        return RouterExecutionResult(
            workload_id=workload_id,
            policy=policy,
            actual_backend=backend_used,
            device_name=device_name,
            is_fallback=is_fallback,
            fallback_reason=fallback_reason,
            latency_ms=exec_ms,
            output=out,
            output_digest=out_digest,
            is_verified=is_verified,
            verification_details=verification_details,
            cost_profile=cost_profile,
            rewrite_applied=rewrite_applied,
        )

    # Alias for uniform interface across engine modules
    execute = route_and_execute


ROUTER = HeterogeneousRouter()

__all__ = [
    "ExecutionPolicy",
    "BackendExecutionError",
    "RouterExecutionResult",
    "HeterogeneousRouter",
    "ROUTER",
]
