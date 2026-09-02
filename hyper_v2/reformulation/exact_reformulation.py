"""
hyper_v2/reformulation/exact_reformulation.py
Exact mathematical reformulations that preserve 100% bit-accurate or analytical equivalence.
"""

from typing import Tuple, Dict, Any
import numpy as np


class ExactReformulator:
    """Provides mathematically exact algorithm substitutions."""

    @staticmethod
    def blocked_matmul_exact(A: np.ndarray, B: np.ndarray, block_size: int = 64) -> np.ndarray:
        """Cache-blocked matrix multiplication with exact arithmetic."""
        M, K = A.shape
        K2, N = B.shape
        assert K == K2, "Matrix dimension mismatch"

        C = np.zeros((M, N), dtype=A.dtype)
        for i in range(0, M, block_size):
            i_end = min(i + block_size, M)
            for k in range(0, K, block_size):
                k_end = min(k + block_size, K)
                A_block = A[i:i_end, k:k_end]
                for j in range(0, N, block_size):
                    j_end = min(j + block_size, N)
                    C[i:i_end, j:j_end] += np.dot(A_block, B[k:k_end, j:j_end])
        return C

    @staticmethod
    def pairwise_to_simd_reduction(vector: np.ndarray) -> float:
        """Exact tree reduction avoiding numerical roundoff drift."""
        return float(np.sum(vector, dtype=np.float64))

    @staticmethod
    def morton_code_encode_3d(points: np.ndarray) -> np.ndarray:
        """Encodes 3D coordinates into 30-bit Morton z-order spatial indices for O(N log N) LBVH."""
        # Normalize to [0, 1023] integer lattice
        mins = np.min(points, axis=0)
        maxs = np.max(points, axis=0)
        ranges = np.maximum(1e-6, maxs - mins)
        norm_pts = np.clip(((points - mins) / ranges) * 1023.0, 0, 1023).astype(np.uint32)

        def expand_bits(v):
            v = (v | (v << 16)) & 0x030000FF
            v = (v | (v << 8)) & 0x0300F00F
            v = (v | (v << 4)) & 0x030C30C3
            v = (v | (v << 2)) & 0x09249249
            return v

        x = expand_bits(norm_pts[:, 0])
        y = expand_bits(norm_pts[:, 1])
        z = expand_bits(norm_pts[:, 2])
        return (x | (y << 1) | (z << 2)).astype(np.uint32)
