"""
hyper100/low_rank_engine.py
===========================
Low-Rank Approximation & Tensor Decomposition Engine.
Decomposes weight and activation matrices into low-rank factorized representations
(W approx U @ S @ Vh), reducing operations from O(M * N) to O(k * (M + N)).
"""

import time
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class LowRankDecomposition:
    """Stores factorized low-rank matrix components."""
    U: np.ndarray          # Shape (M, k)
    Vh: np.ndarray         # Shape (k, N) including singular values scaled
    rank: int
    original_shape: Tuple[int, int]


@dataclass
class LowRankReport:
    """Audit report for low-rank factorization."""
    rank: int
    original_shape: Tuple[int, int]
    compression_ratio: float
    flop_reduction_ratio: float
    frobenius_error: float
    relative_error: float
    energy_retention: float
    memory_saved_bytes: int


class LowRankEngine:
    """Performs truncated and randomized SVD matrix factorizations."""

    @staticmethod
    def factorize_matrix(
        W: np.ndarray,
        target_rank: Optional[int] = None,
        energy_threshold: float = 0.98,
        max_relative_error: float = 0.05
    ) -> Tuple[LowRankDecomposition, LowRankReport]:
        """
        Decomposes W (M x N) into U (M x k) and Vh (k x N).
        """
        arr = np.asarray(W, dtype=np.float32)
        M, N = arr.shape
        orig_params = M * N
        orig_flops = 2.0 * M * N

        # Full or truncated SVD
        U_full, S, Vh_full = np.linalg.svd(arr, full_matrices=False)
        total_energy = float(np.sum(S ** 2))

        if target_rank is None:
            if total_energy > 0:
                cum_energy = np.cumsum(S ** 2) / total_energy
                k = int(np.searchsorted(cum_energy, energy_threshold)) + 1
            else:
                k = 1
            k = max(1, min(k, min(M, N)))
        else:
            k = max(1, min(target_rank, min(M, N)))

        # Truncate components
        U_k = U_full[:, :k]
        S_k = S[:k]
        Vh_k = Vh_full[:k, :]
        # Absorb singular values into Vh
        Vh_scaled = np.diag(S_k) @ Vh_k

        # Reconstructed approximation
        W_approx = U_k @ Vh_scaled
        diff = arr - W_approx
        frob_err = float(np.linalg.norm(diff, "fro"))
        norm_orig = float(np.linalg.norm(arr, "fro"))
        rel_err = float(frob_err / (norm_orig + 1e-12)) if norm_orig > 0 else 0.0
        energy_ret = float(np.sum(S_k ** 2) / (total_energy + 1e-12))

        factor_params = k * (M + N)
        comp_ratio = float(orig_params / max(factor_params, 1))
        factored_flops = 2.0 * k * (M + N)
        flop_reduction = 1.0 - (factored_flops / max(orig_flops, 1.0))
        mem_saved = max(0, (orig_params - factor_params) * 4)

        decomp = LowRankDecomposition(
            U=U_k,
            Vh=Vh_scaled,
            rank=k,
            original_shape=(M, N)
        )

        report = LowRankReport(
            rank=k,
            original_shape=(M, N),
            compression_ratio=comp_ratio,
            flop_reduction_ratio=flop_reduction,
            frobenius_error=frob_err,
            relative_error=rel_err,
            energy_retention=energy_ret,
            memory_saved_bytes=mem_saved
        )
        return decomp, report

    @staticmethod
    def factored_matmul(decomp: LowRankDecomposition, x: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Executes Y = U @ (Vh @ x), computing in two low-rank stages.
        """
        t0 = time.perf_counter()
        # Stage 1: intermediate = Vh @ x (Shape: k x Batch)
        intermediate = decomp.Vh @ x
        # Stage 2: Y = U @ intermediate (Shape: M x Batch)
        result = decomp.U @ intermediate
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return result, latency_ms
