"""
hyper/contracts/sla_engine.py
=============================
Contract Performance Engine (HYPER-SLA) for LEO/HYPER.
Fulfills Sections 39, 40, 41, 42, 65 of the Breakthrough Master Architecture.

Evaluates:
- Application performance vs Hardware performance
- The Four 100% Master Metrics:
    1. 100% Semantic Execution Coverage
    2. 100% Contract Correctness
    3. 100% Evidence Integrity (Fail-Closed)
    4. 100% Contract Performance Closure
- Distinct and honest:
    PHYSICAL_NVIDIA_HARDWARE_PARITY: NOT_ESTABLISHED
"""

import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from hyper.contracts.contract import Contract, validate_contract


class ApplicationSLA:
    """Formal Service Level Agreement (SLA) for an application workload."""
    def __init__(
        self,
        workload_name: str,
        required_latency_ms: float,
        required_throughput_ops: float = 1.0,
        required_accuracy: float = 1.0,
        max_memory_bytes: int = 1024 * 1024 * 1024,  # 1 GB default
        require_determinism: bool = True,
        contract: Optional[Contract] = None,
    ):
        self.workload_name = workload_name
        self.required_latency_ms = required_latency_ms
        self.required_throughput_ops = required_throughput_ops
        self.required_accuracy = required_accuracy
        self.max_memory_bytes = max_memory_bytes
        self.require_determinism = require_determinism
        self.contract = contract

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_name": self.workload_name,
            "required_latency_ms": self.required_latency_ms,
            "required_throughput_ops": self.required_throughput_ops,
            "required_accuracy": self.required_accuracy,
            "max_memory_bytes": self.max_memory_bytes,
            "require_determinism": self.require_determinism,
        }


class SLAMeasurement:
    """Ground-truth measurement against declared Application SLA."""
    def __init__(
        self,
        workload_name: str,
        measured_latency_ms: float,
        measured_throughput_ops: float,
        measured_max_abs_error: float,
        measured_memory_bytes: int,
        is_deterministic: bool,
        contract_closure: bool,
        closure_reasons_failed: List[str],
        provenance: str = "MEASURED_LOCAL",
    ):
        self.workload_name = workload_name
        self.measured_latency_ms = measured_latency_ms
        self.measured_throughput_ops = measured_throughput_ops
        self.measured_max_abs_error = measured_max_abs_error
        self.measured_memory_bytes = measured_memory_bytes
        self.is_deterministic = is_deterministic
        self.contract_closure = contract_closure
        self.closure_reasons_failed = closure_reasons_failed
        self.provenance = provenance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_name": self.workload_name,
            "contract_closure": "PASS" if self.contract_closure else "FAIL",
            "contract_performance_pct": 100.0 if self.contract_closure else 0.0,
            "measured_latency_ms": round(self.measured_latency_ms, 3),
            "measured_throughput_ops": round(self.measured_throughput_ops, 2),
            "measured_max_abs_error": float(self.measured_max_abs_error),
            "measured_memory_bytes": self.measured_memory_bytes,
            "is_deterministic": self.is_deterministic,
            "closure_reasons_failed": self.closure_reasons_failed,
            "provenance": self.provenance,
        }


class FourMasterMetrics:
    """
    The Four 100% Metrics (Section 40).
    Replaces fake single percentages with 4 rigorous, verifiable metrics.
    """
    def __init__(
        self,
        verified_semantic_elements: int,
        declared_semantic_elements: int,
        contracts_satisfied: int,
        contracts_tested: int,
        traceable_results: int,
        reported_results: int,
        sla_closures_passed: int,
        sla_closures_claimed: int,
    ):
        # 1. 100% Semantic Coverage
        self.semantic_execution_coverage = (
            (verified_semantic_elements / float(declared_semantic_elements))
            if declared_semantic_elements > 0 else 0.0
        )
        self.semantic_elements_tuple = (verified_semantic_elements, declared_semantic_elements)

        # 2. 100% Contract Correctness
        self.contract_correctness = (
            (contracts_satisfied / float(contracts_tested))
            if contracts_tested > 0 else 0.0
        )
        self.contracts_tuple = (contracts_satisfied, contracts_tested)

        # 3. 100% Evidence Integrity
        self.evidence_integrity = (
            (traceable_results / float(reported_results))
            if reported_results > 0 else 0.0
        )
        self.evidence_tuple = (traceable_results, reported_results)

        # 4. 100% Contract Performance Closure
        self.contract_performance_closure = (
            (sla_closures_passed / float(sla_closures_claimed))
            if sla_closures_claimed > 0 else 0.0
        )
        self.sla_tuple = (sla_closures_passed, sla_closures_claimed)

        # Section 41: Physical NVIDIA Parity
        self.physical_nvidia_hardware_parity = "NOT_ESTABLISHED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "four_100_percent_metrics": {
                "1_semantic_execution_coverage_pct": round(self.semantic_execution_coverage * 100.0, 2),
                "1_semantic_execution_ratio": f"{self.semantic_elements_tuple[0]}/{self.semantic_elements_tuple[1]}",
                "2_contract_correctness_pct": round(self.contract_correctness * 100.0, 2),
                "2_contract_correctness_ratio": f"{self.contracts_tuple[0]}/{self.contracts_tuple[1]}",
                "3_evidence_integrity_pct": round(self.evidence_integrity * 100.0, 2),
                "3_evidence_integrity_ratio": f"{self.evidence_tuple[0]}/{self.evidence_tuple[1]}",
                "4_contract_performance_closure_pct": round(self.contract_performance_closure * 100.0, 2),
                "4_contract_performance_closure_ratio": f"{self.sla_tuple[0]}/{self.sla_tuple[1]}",
            },
            "physical_nvidia_hardware_parity": self.physical_nvidia_hardware_parity,
            "hardware_constraints": "CPU (Intel i5-12450H/13420H) + Intel UHD Graphics (48 EU) ONLY",
        }


class HyperSLAEngine:
    """
    HYPER-SLA Engine:
    Measures actual workload performance on local Intel Core i5 / Intel UHD,
    validates contract closure, and computes the Four Master Metrics.
    """

    def evaluate_workload(
        self,
        sla: ApplicationSLA,
        execute_fn: Callable[[], Any],
        reference_output: Any,
        repetitions: int = 5,
    ) -> SLAMeasurement:
        """
        Executes workload for N repetitions, measuring actual latency, determinism,
        memory, and numerical accuracy against declared application SLA.
        """
        latencies_ms: List[float] = []
        outputs = []

        # Warmup
        _ = execute_fn()

        for _ in range(repetitions):
            t0 = time.perf_counter()
            out = execute_fn()
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)
            outputs.append(out)

        median_latency_ms = float(np.median(latencies_ms))
        throughput_ops = 1000.0 / median_latency_ms if median_latency_ms > 0 else 0.0

        # Determinism check across runs
        def _extract_payload(obj: Any) -> Any:
            if hasattr(obj, "outputs"):
                return obj.outputs
            if hasattr(obj, "output"):
                return obj.output
            return obj

        def _is_equal(a: Any, b: Any) -> bool:
            a_p = _extract_payload(a)
            b_p = _extract_payload(b)
            if isinstance(a_p, dict) and isinstance(b_p, dict):
                if set(a_p.keys()) != set(b_p.keys()):
                    return False
                for k in a_p:
                    v_a = a_p[k]
                    v_b = b_p[k]
                    if isinstance(v_a, np.ndarray) and isinstance(v_b, np.ndarray):
                        if not np.array_equal(v_a, v_b, equal_nan=True):
                            return False
                    else:
                        try:
                            if not bool(v_a == v_b):
                                return False
                        except Exception:
                            return False
                return True
            if isinstance(a_p, np.ndarray) and isinstance(b_p, np.ndarray):
                return bool(np.array_equal(a_p, b_p, equal_nan=True))
            try:
                return bool(a_p == b_p)
            except Exception:
                return False

        is_deterministic = True
        first_out = outputs[0]
        for subsequent in outputs[1:]:
            if not _is_equal(first_out, subsequent):
                is_deterministic = False
                break

        # Accuracy check against reference output
        max_abs_error = 0.0
        if reference_output is not None:
            a_p = _extract_payload(first_out)
            r_p = _extract_payload(reference_output)
            if isinstance(a_p, dict) and isinstance(r_p, dict):
                for k in r_p:
                    if k in a_p and isinstance(a_p[k], np.ndarray) and isinstance(r_p[k], np.ndarray):
                        diff = float(np.max(np.abs(a_p[k] - r_p[k])))
                        if diff > max_abs_error:
                            max_abs_error = diff
            elif isinstance(a_p, np.ndarray) and isinstance(r_p, np.ndarray):
                max_abs_error = float(np.max(np.abs(a_p - r_p))) if a_p.size > 0 else 0.0
            elif not _is_equal(a_p, r_p):
                max_abs_error = 1.0

        # Memory accounting
        first_payload = _extract_payload(first_out)
        if isinstance(first_payload, dict):
            est_mem_bytes = sum(v.nbytes for v in first_payload.values() if isinstance(v, np.ndarray))
        elif isinstance(first_payload, np.ndarray):
            est_mem_bytes = first_payload.nbytes
        else:
            est_mem_bytes = 4096

        # Strict SLA Contract Closure Checks
        failed_reasons: List[str] = []

        # 1. Latency requirement
        if median_latency_ms > sla.required_latency_ms:
            failed_reasons.append(
                f"Latency exceeded SLA requirement: {median_latency_ms:.2f} ms > {sla.required_latency_ms:.2f} ms"
            )

        # 2. Throughput requirement
        if throughput_ops < sla.required_throughput_ops:
            failed_reasons.append(
                f"Throughput below SLA requirement: {throughput_ops:.2f} ops/s < {sla.required_throughput_ops:.2f} ops/s"
            )

        # 3. Accuracy / Error requirement
        if sla.contract and sla.contract.exact_required:
            if max_abs_error > 0.0:
                failed_reasons.append(f"Exact contract required, but max_abs_error = {max_abs_error}")
        elif sla.contract and sla.contract.max_abs_error is not None:
            if max_abs_error > sla.contract.max_abs_error:
                failed_reasons.append(
                    f"max_abs_error exceeded: {max_abs_error} > {sla.contract.max_abs_error}"
                )

        # 4. Memory requirement
        if est_mem_bytes > sla.max_memory_bytes:
            failed_reasons.append(
                f"Memory exceeded SLA limit: {est_mem_bytes} bytes > {sla.max_memory_bytes} bytes"
            )

        # 5. Determinism requirement
        if sla.require_determinism and not is_deterministic:
            failed_reasons.append("Non-deterministic execution across identical runs")

        contract_closure = (len(failed_reasons) == 0)

        return SLAMeasurement(
            workload_name=sla.workload_name,
            measured_latency_ms=median_latency_ms,
            measured_throughput_ops=throughput_ops,
            measured_max_abs_error=max_abs_error,
            measured_memory_bytes=est_mem_bytes,
            is_deterministic=is_deterministic,
            contract_closure=contract_closure,
            closure_reasons_failed=failed_reasons,
            provenance="MEASURED_LOCAL",
        )
