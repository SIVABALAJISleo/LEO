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
    task_type: str = "GEMM"  # GEMM | FFT | RENDERING | INFERENCE
    perceptual_metric: Optional[str] = None
    functional_metric: Optional[str] = None
    k: int = 5


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
            fallback="full_computation",
            perceptual_metric=workload_spec.perceptual_metric,
            functional_metric=workload_spec.functional_metric,
            k=workload_spec.k,
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
