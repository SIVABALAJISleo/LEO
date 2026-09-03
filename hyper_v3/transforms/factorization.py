"""
hyper_v3/transforms/factorization.py
Randomized SVD low-rank matrix decomposition and BitNet 1.58b ternary quantization.
"""

from typing import Tuple, Optional
import numpy as np


class FactorizationTransformer:
    """Computes low-rank approximations and ternary quantizations."""

    @staticmethod
    def randomized_svd(matrix: np.ndarray, rank: int, n_iter: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """Decomposes A ~ U @ V with rank r, replacing O(m*n*k) with O(r*(m+n)*k)."""
        m, n = matrix.shape
        rank = min(rank, m, n)
        omega = np.random.randn(n, rank).astype(matrix.dtype)
        y = matrix @ omega
        for _ in range(n_iter):
            y = matrix @ (matrix.T @ y)
        q, _ = np.linalg.qr(y)
        b = q.T @ matrix
        u_tilde, s, vh = np.linalg.svd(b, full_matrices=False)
        u = q @ u_tilde[:, :rank]
        v = np.diag(s[:rank]) @ vh[:rank, :]
        return u, v

    @staticmethod
    def bitnet_ternary_quantize(weights: np.ndarray) -> Tuple[np.ndarray, float]:
        """Quantizes weights into {-1, 0, +1} with an FP32 scale factor."""
        gamma = float(np.mean(np.abs(weights)))
        if gamma == 0:
            return np.zeros_like(weights, dtype=np.int8), 1.0
        scaled = weights / gamma
        quantized = np.clip(np.round(scaled), -1, 1).astype(np.int8)
        return quantized, gamma
