"""
hyper/reconstruction/reconstruction_engine.py
=============================================
Compressed Sensing & Multiresolution Reconstruction Engine.
Uses Orthogonal Matching Pursuit (OMP) to recover sparse signals from M << N measurements.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple


class ReconstructionEngine:
    """
    Recovers sparse signals via sublinear compressed measurements.
    """
    def __init__(self, max_iter: int = 16):
        self.max_iter = max_iter

    def reconstruct_omp(
        self, y: np.ndarray, Phi: np.ndarray, sparsity_k: int = 4
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Orthogonal Matching Pursuit to solve: y = Phi @ x for sparse x
        """
        t0 = time.perf_counter()
        M, N = Phi.shape
        residual = y.copy()
        support = []
        x_hat = np.zeros(N, dtype=y.dtype)

        for _ in range(min(sparsity_k, self.max_iter)):
            correlations = Phi.T @ residual
            best_idx = int(np.argmax(np.abs(correlations)))
            if best_idx not in support:
                support.append(best_idx)
            
            Phi_sub = Phi[:, support]
            x_sub, _, _, _ = np.linalg.lstsq(Phi_sub, y, rcond=None)
            residual = y - Phi_sub @ x_sub
            
            if np.linalg.norm(residual) < 1e-6:
                break

        for idx, val in zip(support, x_sub):
            x_hat[idx] = val

        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return x_hat, {
            "measurements_M": M,
            "signal_dim_N": N,
            "sparsity_k": sparsity_k,
            "recovered_support_len": len(support),
            "reconstruction_time_ms": round(t_elapsed_ms, 3)
        }
