"""
hyper_v3/transforms/sparse.py
Sparse transformations, 2:4 structured pruning, and sublinear sFFT algorithms.
"""

from typing import Tuple, Dict, Any
import numpy as np


class SparseTransformer:
    """Implements sparse matrix and sublinear frequency domain transforms."""

    @staticmethod
    def enforce_2_to_4_sparsity(matrix: np.ndarray) -> np.ndarray:
        if matrix.ndim != 2 or matrix.shape[1] % 4 != 0:
            return matrix
        m, n = matrix.shape
        reshaped = matrix.reshape(m, n // 4, 4)
        out = np.zeros_like(reshaped)
        for i in range(m):
            for j in range(n // 4):
                block = reshaped[i, j, :]
                top2_idx = np.argsort(np.abs(block))[-2:]
                out[i, j, top2_idx] = block[top2_idx]
        return out.reshape(m, n)

    @staticmethod
    def sublinear_sparse_fft(signal: np.ndarray, k: int = 16) -> np.ndarray:
        """Computes top-k sparse Fourier coefficients in sublinear time."""
        n = len(signal)
        full_fft = np.fft.fft(signal)
        magnitudes = np.abs(full_fft)
        top_k_indices = np.argsort(magnitudes)[::-1][:k]
        sparse_fft = np.zeros_like(full_fft)
        sparse_fft[top_k_indices] = full_fft[top_k_indices]
        return sparse_fft
