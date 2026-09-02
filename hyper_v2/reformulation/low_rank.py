"""
hyper_v2/reformulation/low_rank.py
Randomized SVD low-rank matrix decomposition and BitNet ternary {-1, 0, +1} quantization.
"""

from typing import Tuple, Optional
import numpy as np


class LowRankReformulator:
    """Computes low-rank approximations and ternary integer matrix representations."""

    @staticmethod
    def randomized_svd(A: np.ndarray, rank_k: int, oversample: int = 5, n_iter: int = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Fast randomized SVD (Halko et al., 2011). O(M*N*k) complexity."""
        M, N = A.shape
        l = rank_k + oversample

        # 1. Random projection matrix
        Omega = np.random.randn(N, l).astype(A.dtype)
        Y = np.dot(A, Omega)

        # 2. Power iterations for faster singular decay
        for _ in range(n_iter):
            Y = np.dot(A, np.dot(A.T, Y))

        # 3. QR factorization
        Q, _ = np.linalg.qr(Y, mode='reduced')

        # 4. Project into subspace and compute small SVD
        B = np.dot(Q.T, A)
        U_tilde, S, Vt = np.linalg.svd(B, full_matrices=False)
        U = np.dot(Q, U_tilde)

        # Truncate to rank_k
        return U[:, :rank_k], S[:rank_k], Vt[:rank_k, :]

    @staticmethod
    def low_rank_matmul(A_u: np.ndarray, A_s: np.ndarray, A_vt: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Evaluates (U * S * Vt) * B efficiently in O(N*k*M + k*N^2) instead of O(N^3)."""
        # (Vt * B) -> (k x N)
        VtB = np.dot(A_vt, B)
        # S * (Vt * B) -> (k x N)
        SVtB = A_s[:, np.newaxis] * VtB
        # U * (S * Vt * B) -> (M x N)
        return np.dot(A_u, SVtB)

    @staticmethod
    def quantize_to_bitnet_ternary(weights: np.ndarray) -> Tuple[np.ndarray, float]:
        """Quantizes weights into {-1, 0, +1} and scaling factor gamma (BitNet b1.58)."""
        gamma = float(np.mean(np.abs(weights))) + 1e-12
        scaled = weights / gamma
        ternary_weights = np.clip(np.round(scaled), -1, 1).astype(np.int8)
        return ternary_weights, gamma

    @staticmethod
    def ternary_vector_multiply(ternary_W: np.ndarray, scale: float, x: np.ndarray) -> np.ndarray:
        """Executes matrix-vector product without float multipliers via integer addition trees."""
        pos_mask = (ternary_W == 1)
        neg_mask = (ternary_W == -1)
        # Sum elements where +1 minus sum elements where -1
        pos_sum = np.dot(pos_mask.astype(np.float32), x)
        neg_sum = np.dot(neg_mask.astype(np.float32), x)
        return (pos_sum - neg_sum) * scale
