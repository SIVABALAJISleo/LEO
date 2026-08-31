"""
hyper/low_rank/low_rank_engine.py
=================================
Low-Rank Factorization & Randomized SVD Engine:
- Fast Randomized Subspace Projection (Halko, Martinsson, Tropp 2011)
- Factorized computation: A @ B ≈ (A_L @ A_R) @ B = A_L @ (A_R @ B)
- Reduces O(N^3) to O(NKr)
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, Optional


class LowRankEngine:
    """
    Computes low-rank tensor/matrix approximations with error bounding.
    """
    def __init__(self, default_rank: int = 16):
        self.default_rank = default_rank

    def factorize_randomized_svd(
        self, A: np.ndarray, rank: Optional[int] = None, oversample: int = 4
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Computes Low-Rank Factors U_r, V_r such that A ≈ U_r @ V_r
        """
        t0 = time.perf_counter()
        M, K = A.shape
        r = min(rank or self.default_rank, min(M, K))
        l = r + oversample

        rng = np.random.RandomState(42)
        Omega = rng.randn(K, l).astype(A.dtype)
        Y = A @ Omega
        Q, _ = np.linalg.qr(Y)
        B = Q.T @ A
        U_hat, s, Vt = np.linalg.svd(B, full_matrices=False)
        
        U_r = Q @ U_hat[:, :r] * s[:r]
        V_r = Vt[:r, :]
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Relative Frobenius error estimation
        A_recon = U_r @ V_r
        rel_frob_error = float(np.linalg.norm(A - A_recon) / max(1e-12, np.linalg.norm(A)))

        return U_r, V_r, {
            "rank": r,
            "relative_frobenius_error": round(rel_frob_error, 6),
            "factorization_time_ms": round(t_elapsed_ms, 3)
        }

    def execute_low_rank_matmul(
        self, U_r: np.ndarray, V_r: np.ndarray, B: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes factorized chain: U_r @ (V_r @ B)
        FLOPs: 2 * r * K * N + 2 * M * r * N = 2 * r * N * (M + K) << 2 * M * K * N
        """
        t0 = time.perf_counter()
        VrB = V_r @ B
        C = U_r @ VrB
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        M = U_r.shape[0]
        r = U_r.shape[1]
        K = V_r.shape[1]
        N = B.shape[1]

        flops_dense = 2 * M * K * N
        flops_low_rank = 2 * r * N * (M + K)
        cer = 1.0 - (flops_low_rank / max(1, flops_dense))

        return C, {
            "flops_dense": flops_dense,
            "flops_low_rank": flops_low_rank,
            "cer": round(cer, 4),
            "elapsed_ms": round(t_elapsed_ms, 3)
        }
