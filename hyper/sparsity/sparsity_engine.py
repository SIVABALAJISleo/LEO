"""
hyper/sparsity/sparsity_engine.py
=================================
Overhead-Aware Sparsity Engine for LEO/HYPER.
Fulfills Phase 7 of the Master Architectural Specification.
Guarantees that sparse execution is chosen only when:
    T_threshold + T_sparse + T_verify < T_dense
and mathematical or contractual error limits are satisfied.
"""

import time
from typing import Any, Dict, Optional, Tuple
import numpy as np
import scipy.sparse as sp


class SparsityEngine:
    """
    Evaluates, benchmarks, and executes sparsity-exploiting matrix routines
    with measured overhead accounting.
    """

    def __init__(self, default_threshold: float = 1e-5):
        self.default_threshold = default_threshold

    def evaluate_sparsity(self, matrix: np.ndarray, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze zero and sub-threshold element proportions in a matrix.
        """
        tau = threshold if threshold is not None else self.default_threshold
        t0 = time.perf_counter_ns()
        zero_mask = np.abs(matrix) <= tau
        t_thresh_ns = time.perf_counter_ns() - t0

        zero_count = int(np.sum(zero_mask))
        total_elements = matrix.size
        density = float((total_elements - zero_count) / max(1, total_elements))
        sparsity = float(zero_count / max(1, total_elements))

        return {
            "threshold": tau,
            "total_elements": total_elements,
            "zero_elements": zero_count,
            "density": density,
            "sparsity": sparsity,
            "sparsity_pct": round(sparsity * 100.0, 2),
            "thresholding_cost_ms": t_thresh_ns / 1e6,
        }

    def execute_with_overhead_check(
        self,
        A: np.ndarray,
        B: np.ndarray,
        threshold: Optional[float] = None,
        max_allowed_error: Optional[float] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Conditionally execute sparse matmul only when proven faster than dense
        and compliant with error bounds:
            T_threshold + T_sparse + T_verify < T_dense
        """
        tau = threshold if threshold is not None else self.default_threshold

        # 1. Measure dense execution
        t0 = time.perf_counter_ns()
        C_dense = A @ B
        t_dense_ms = (time.perf_counter_ns() - t0) / 1e6

        # 2. Measure thresholding cost
        t_th_start = time.perf_counter_ns()
        A_thresh = np.where(np.abs(A) <= tau, 0.0, A)
        t_thresh_ms = (time.perf_counter_ns() - t_th_start) / 1e6

        # Calculate density
        nnz = int(np.count_nonzero(A_thresh))
        density = nnz / max(1, A.size)
        sparsity = 1.0 - density

        # 3. Measure sparse conversion and execution
        t_sp_start = time.perf_counter_ns()
        A_sparse = sp.csr_matrix(A_thresh)
        C_sparse = A_sparse.dot(B)
        t_sparse_ms = (time.perf_counter_ns() - t_sp_start) / 1e6

        # 4. Measure verification cost & error
        t_ver_start = time.perf_counter_ns()
        max_abs_err = float(np.max(np.abs(C_dense - C_sparse)))
        t_verify_ms = (time.perf_counter_ns() - t_ver_start) / 1e6

        total_sparse_pipeline_ms = t_thresh_ms + t_sparse_ms + t_verify_ms

        error_satisfied = True
        if max_allowed_error is not None and max_abs_err > max_allowed_error:
            error_satisfied = False

        faster_than_dense = total_sparse_pipeline_ms < t_dense_ms

        use_sparse = faster_than_dense and error_satisfied

        telemetry = {
            "threshold": tau,
            "density": density,
            "sparsity": sparsity,
            "thresholding_cost_ms": t_thresh_ms,
            "sparse_execution_cost_ms": t_sparse_ms,
            "verification_cost_ms": t_verify_ms,
            "total_sparse_pipeline_ms": total_sparse_pipeline_ms,
            "dense_execution_cost_ms": t_dense_ms,
            "max_abs_error": max_abs_err,
            "faster_than_dense": faster_than_dense,
            "error_satisfied": error_satisfied,
            "path_chosen": "REDUCED_WORK" if (use_sparse and max_abs_err == 0.0) else (
                "NUMERICALLY_APPROXIMATE" if use_sparse else "EXACT"
            ),
        }

        if use_sparse:
            return C_sparse, telemetry
        else:
            return C_dense, telemetry
