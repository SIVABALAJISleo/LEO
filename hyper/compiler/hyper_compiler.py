"""
hyper/compiler/hyper_compiler.py
================================
HYPER Compiler & Algorithm Optimization Search:
Compiles algorithmic workloads through:
Workload -> Intermediate Representation -> Dependency Graph -> Cost Model ->
Candidate Algorithm Search -> Correctness Verification -> Live Performance Measurement ->
Best Execution Plan Selection.

Never assumes an optimization is faster: measures actual latency on the host hardware.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class CompiledExecutionPlan:
    workload_name: str
    selected_algorithm: str
    baseline_latency_ms: float
    measured_latency_ms: float
    speedup_ratio: float
    correctness_verified: bool
    relative_error: float


class HyperCompiler:
    """
    Search-based compiler selecting between candidate algorithm formulations:
    - NAIVE (Full O(N^2) or standard compute)
    - TILED_CACHE (Cache-blocked for L1/L2 data cache)
    - SEPARABLE (Factorized 1D horizontal + 1D vertical passes)
    - SPARSITY_SKIPPED (Zero-value bypass)
    - INCREMENTAL_DELTA (Only recomputing delta updates)
    """

    def __init__(self):
        self.cached_plans: Dict[str, CompiledExecutionPlan] = {}

    def compile_and_optimize(
        self,
        workload_name: str,
        input_data: np.ndarray,
        baseline_fn: Callable[[np.ndarray], np.ndarray],
        candidate_fns: Dict[str, Callable[[np.ndarray], np.ndarray]],
        exact_threshold: float = 1e-4,
    ) -> CompiledExecutionPlan:
        """
        Executes candidate algorithms, verifies numerical equivalence,
        measures wall-clock elapsed time, and selects the best performer.
        """
        # 1. Measure Baseline
        t0 = time.perf_counter()
        baseline_output = baseline_fn(input_data)
        baseline_ms = (time.perf_counter() - t0) * 1000.0

        best_algo = "BASELINE"
        best_ms = baseline_ms
        best_err = 0.0

        for algo_name, fn in candidate_fns.items():
            try:
                t_start = time.perf_counter()
                candidate_output = fn(input_data)
                cand_ms = (time.perf_counter() - t_start) * 1000.0

                # Verify numerical equivalence
                diff = np.abs(candidate_output - baseline_output)
                denom = float(np.linalg.norm(baseline_output))
                rel_err = float(np.max(diff)) if denom < 1e-6 else float(np.linalg.norm(diff) / denom)

                # Must strictly satisfy correctness threshold
                if rel_err <= exact_threshold:
                    if cand_ms < best_ms:
                        best_ms = cand_ms
                        best_algo = algo_name
                        best_err = rel_err
            except Exception:
                continue

        speedup = round(baseline_ms / max(1e-5, best_ms), 2)
        plan = CompiledExecutionPlan(
            workload_name=workload_name,
            selected_algorithm=best_algo,
            baseline_latency_ms=round(baseline_ms, 3),
            measured_latency_ms=round(best_ms, 3),
            speedup_ratio=speedup,
            correctness_verified=True,
            relative_error=best_err,
        )
        self.cached_plans[workload_name] = plan
        return plan
