"""
backend/caoe/contract_analyzer.py
=================================
CAOE Layer 1: Contract Detection & Tolerance Sweeping.

Learns and infers what the application actually needs:
- Analyzes workload dimensions, types, sensitivity, and acceptable error bounds.
- Sweeps the Pareto frontier across precision (32, 16, 8) and sparsity (0% to 90%).
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


@dataclasses.dataclass
class WorkloadSpec:
    name: str
    shape: Tuple[int, ...]
    dtype: np.dtype = np.dtype("float32")
    sample_inputs: List[np.ndarray] = dataclasses.field(default_factory=list)
    task_type: str = "GEMM"  # GEMM | FFT | RENDERING | INFERENCE | CRYPTO
    perceptual_metric: Optional[str] = None
    functional_metric: Optional[str] = None
    k: int = 5
    max_memory_mb: float = 12000.0  # 12 GB hard safety cap for Lenovo IdeaPad Slim 3
    exactness_class: str = "NUMERICALLY_EQUIVALENT"


@dataclasses.dataclass
class Contract:
    name: str
    input_shape: Tuple[int, ...]
    output_type: str
    tolerance: Dict[str, Any]
    precision_options: List[int]
    precision: int = 32
    sparsity_tolerance: float = 0.0
    cache_ttl: float = 0.0
    fallback: str = "full_computation"
    perceptual_metric: Optional[str] = None
    functional_metric: Optional[str] = None
    k: int = 5
    max_memory_mb: float = 12000.0
    exactness_class: str = "NUMERICALLY_EQUIVALENT"
    shannon_entropy: float = 0.0
    routing_recommendation: str = "ONLINE_PHASE_TRANSITION_SUBSUMPTION"
    is_admissible: bool = True
    boundary_note: Optional[str] = None

    def update(self, best_option: Dict[str, Any]) -> None:
        if "precision" in best_option:
            self.precision = best_option["precision"]
        if "sparsity" in best_option:
            self.sparsity_tolerance = best_option["sparsity"]


class ContractAnalyzer:
    """Learn what the application actually needs."""

    @staticmethod
    def analyze_workload(workload_spec: WorkloadSpec) -> Contract:
        # Infer default tolerances based on task type
        rel_tol = 1e-4
        cache_ttl = 0.0
        if workload_spec.task_type == "RENDERING":
            rel_tol = 1e-2
            cache_ttl = 5.0
        elif workload_spec.task_type == "INFERENCE":
            rel_tol = 5e-3
            cache_ttl = 60.0
        elif workload_spec.task_type == "FFT":
            rel_tol = 1e-6
            cache_ttl = 0.0
        elif workload_spec.task_type == "CRYPTO":
            rel_tol = 0.0
            cache_ttl = 0.0

        # Pre-flight Memory and Entropy Inspection
        from backend.hardware.universal_subsumption_engine import UniversalSubsumptionEngine

        inputs_dict: Dict[str, Any] = {}
        if workload_spec.sample_inputs:
            for idx, arr in enumerate(workload_spec.sample_inputs):
                inputs_dict[f"input_{idx}"] = arr
        else:
            # Estimate footprint from shape and dtype
            elem_count = 1
            for dim in workload_spec.shape:
                elem_count *= dim
            itemsize = np.dtype(workload_spec.dtype).itemsize
            est_bytes = elem_count * itemsize
            est_mb = est_bytes / (1024.0 * 1024.0)
            if est_mb > workload_spec.max_memory_mb:
                inputs_dict["synthetic_payload"] = b"\x00" * int(min(1024 * 1024, est_bytes))
                # Explicit trigger of memory barrier
                inputs_dict["_declared_bytes"] = est_bytes

        # If declared bytes exceeds max_memory_mb
        declared_bytes = inputs_dict.pop("_declared_bytes", None)
        if declared_bytes is not None and (declared_bytes / (1024.0 * 1024.0)) > workload_spec.max_memory_mb:
            is_admissible = False
            mem_mb = declared_bytes / (1024.0 * 1024.0)
            entropy = 0.0
            route_rec = f"PHYSICAL_ENVELOPE_EXCEEDED: Requested {mem_mb:.1f} MB exceeds hard 12 GB safety cap ({workload_spec.max_memory_mb} MB)."
        elif inputs_dict:
            is_admissible, mem_mb, entropy, route_rec = UniversalSubsumptionEngine.preflight_contract_and_memory_guard(
                inputs_dict, max_memory_mb=workload_spec.max_memory_mb
            )
        else:
            is_admissible, mem_mb, entropy, route_rec = True, 0.0, 0.0, "ONLINE_PHASE_TRANSITION_SUBSUMPTION"

        if rel_tol == 0.0 or entropy > 0.85:
            route_rec = "NATIVE_EXACT_AVX2_OPENCL_USM"

        contract = Contract(
            name=workload_spec.name,
            input_shape=workload_spec.shape,
            output_type=str(workload_spec.dtype),
            tolerance={
                "absolute_error": rel_tol,
                "relative_error": rel_tol,
                "perceptual_metric": 0.99 if workload_spec.perceptual_metric else None,
                "functional_metric": 0.95 if workload_spec.functional_metric else None,
            },
            precision_options=[32, 16, 8],
            precision=32,
            sparsity_tolerance=0.0,
            cache_ttl=cache_ttl,
            fallback="native_exact" if route_rec == "NATIVE_EXACT_AVX2_OPENCL_USM" else "full_computation",
            perceptual_metric=workload_spec.perceptual_metric,
            functional_metric=workload_spec.functional_metric,
            k=workload_spec.k,
            max_memory_mb=workload_spec.max_memory_mb,
            exactness_class=workload_spec.exactness_class,
            shannon_entropy=entropy,
            routing_recommendation=route_rec,
            is_admissible=is_admissible,
            boundary_note=route_rec if not is_admissible else None,
        )
        return contract

    @staticmethod
    def sweep_tolerance(
        computation_fn: Callable[[np.ndarray, int, float], np.ndarray],
        sample_input: np.ndarray,
        reference_output: np.ndarray,
        threshold: float = 1e-2,
    ) -> List[Dict[str, Any]]:
        """
        Run computation at combinations of precision and sparsity.
        Measure error vs performance to locate the Pareto frontier.
        """
        results = []

        # Baseline execution time (FP32, 0 sparsity)
        t0 = time.perf_counter_ns()
        _ = computation_fn(sample_input, 32, 0.0)
        baseline_ms = max(1e-6, (time.perf_counter_ns() - t0) / 1e6)

        precisions = [32, 16, 8]
        sparsities = [0.0, 0.25, 0.5, 0.75, 0.9]

        for prec in precisions:
            for sp in sparsities:
                t_start = time.perf_counter_ns()
                cand_out = computation_fn(sample_input, prec, sp)
                cand_ms = max(1e-6, (time.perf_counter_ns() - t_start) / 1e6)

                speedup = baseline_ms / cand_ms

                # Measure relative error
                diff = np.abs(cand_out.astype(np.float64) - reference_output.astype(np.float64))
                ref_abs = np.abs(reference_output.astype(np.float64))
                with np.errstate(divide="ignore", invalid="ignore"):
                    rel = np.where(ref_abs > 0, diff / ref_abs, diff)
                error = float(np.max(rel)) if rel.size > 0 else 0.0

                acceptable = bool(error <= threshold)

                results.append({
                    "precision": prec,
                    "sparsity": sp,
                    "speedup": round(speedup, 2),
                    "error": error,
                    "acceptable": acceptable,
                })

        return results
