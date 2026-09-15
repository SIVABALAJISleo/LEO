"""
hyper/low_rank/low_rank_engine.py
=================================
Low-Rank Factorization & Break-Even Analysis Engine for LEO/HYPER.
Fulfills Phase 8 of the Master Architectural Specification.
Guarantees that decomposition overhead is honestly measured and accounted for.
"""

import math
import time
from typing import Any, Dict, Optional, Tuple
import numpy as np


class LowRankEngine:
    """
    Evaluates, decomposes, and executes low-rank approximations
    with complete overhead accounting and break-even reuse analysis.
    """

    def __init__(self, default_rank: int = 16):
        self.default_rank = default_rank

    def factorize(
        self, A: np.ndarray, rank: Optional[int] = None, oversample: int = 4
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Factorize A ≈ U_r @ V_r using randomized SVD.
        Measures factorization time and reconstruction residual.
        """
        t0 = time.perf_counter_ns()
        M, K = A.shape
        r = min(rank or self.default_rank, min(M, K))
        l = min(r + oversample, min(M, K))

        rng = np.random.RandomState(42)
        Omega = rng.randn(K, l).astype(A.dtype)
        Y = A @ Omega
        Q, _ = np.linalg.qr(Y)
        B = Q.T @ A
        U_hat, s, Vt = np.linalg.svd(B, full_matrices=False)

        U_r = Q @ U_hat[:, :r] * s[:r]
        V_r = Vt[:r, :]
        t_factor_ms = (time.perf_counter_ns() - t0) / 1e6

        # Measure reconstruction cost and residual norm
        t_rec_start = time.perf_counter_ns()
        A_recon = U_r @ V_r
        t_recon_ms = (time.perf_counter_ns() - t_rec_start) / 1e6

        residual_matrix = A - A_recon
        residual_norm = float(np.linalg.norm(residual_matrix))
        a_norm = float(np.linalg.norm(A))
        rel_error = float(residual_norm / max(1e-12, a_norm))

        meta = {
            "rank": r,
            "factorization_cost_ms": t_factor_ms,
            "reconstruction_cost_ms": t_recon_ms,
            "residual_norm": residual_norm,
            "relative_error": rel_error,
        }
        return U_r, V_r, meta

    def benchmark_and_execute(
        self,
        A: np.ndarray,
        B: np.ndarray,
        rank: Optional[int] = None,
        expected_reuse_count: int = 1,
        max_allowed_rel_error: Optional[float] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Execute matrix multiplication honestly comparing dense vs low-rank.
        Calculates break-even reuse count and respects error bounds.
        """
        # 1. Measure single dense execution
        t_dense_start = time.perf_counter_ns()
        C_dense = A @ B
        t_dense_ms = (time.perf_counter_ns() - t_dense_start) / 1e6

        # 2. Factorize A
        U_r, V_r, factor_meta = self.factorize(A, rank=rank)
        t_factor_ms = factor_meta["factorization_cost_ms"]
        rel_error = factor_meta["relative_error"]

        # 3. Measure single low-rank chain: U_r @ (V_r @ B)
        t_lr_start = time.perf_counter_ns()
        C_lr = U_r @ (V_r @ B)
        t_lr_ms = (time.perf_counter_ns() - t_lr_start) / 1e6

        # 4. Compute break-even reuse count
        savings_per_run = t_dense_ms - t_lr_ms
        if savings_per_run > 0:
            break_even_count = math.ceil(t_factor_ms / savings_per_run)
        else:
            break_even_count = float("inf")

        # 5. Check total cost for expected reuse count
        total_lr_cost = t_factor_ms + (expected_reuse_count * t_lr_ms)
        total_dense_cost = expected_reuse_count * t_dense_ms

        error_acceptable = True
        if max_allowed_rel_error is not None and rel_error > max_allowed_rel_error:
            error_acceptable = False

        worthwhile = (total_lr_cost < total_dense_cost) and error_acceptable

        telemetry = {
            "rank": factor_meta["rank"],
            "factorization_cost_ms": t_factor_ms,
            "reconstruction_cost_ms": factor_meta["reconstruction_cost_ms"],
            "residual_norm": factor_meta["residual_norm"],
            "relative_error": rel_error,
            "dense_runtime_ms": t_dense_ms,
            "low_rank_runtime_ms": t_lr_ms,
            "break_even_reuse_count": break_even_count,
            "expected_reuse_count": expected_reuse_count,
            "total_low_rank_cost_ms": total_lr_cost,
            "total_dense_cost_ms": total_dense_cost,
            "error_acceptable": error_acceptable,
            "is_beneficial": worthwhile,
            "path_class": "NUMERICALLY_APPROXIMATE" if worthwhile else "EXACT",
        }

        if worthwhile:
            return C_lr, telemetry
        else:
            return C_dense, telemetry
