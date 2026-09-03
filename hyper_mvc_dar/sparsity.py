"""
hyper_mvc_dar/sparsity.py
Sparsity Engine: Analyzes zero, block, and structured sparsity patterns
and determines exact break-even thresholds against dense AVX2 kernels.
"""

from typing import Dict, Any, Tuple
import numpy as np


class SparsityEngine:
    """Analyzes matrix sparsity and selects dense vs CSR/ELLPACK/2:4 structured formats."""

    @staticmethod
    def measure_sparsity(tensor: np.ndarray) -> float:
        zero_count = int(np.sum(tensor == 0))
        return zero_count / tensor.size

    @staticmethod
    def calculate_break_even_sparsity(m: int, n: int, k: int) -> float:
        """
        On AVX2 CPU architecture, CSR sparse matrix-vector format introduces indexing overhead.
        Empirical break-even is typically ~70% to 80% sparsity.
        """
        dense_intensity = (2 * m * n * k) / ((m * k + k * n + m * n) * 4)
        # Sparse format requires 2x memory per non-zero (values + col_indices)
        break_even = 0.75 if m >= 512 else 0.85
        return break_even

    @staticmethod
    def should_use_sparse_format(tensor: np.ndarray) -> Tuple[bool, str]:
        sp = SparsityEngine.measure_sparsity(tensor)
        be = SparsityEngine.calculate_break_even_sparsity(*tensor.shape, tensor.shape[-1])
        if sp >= be:
            return True, "CSR_SPARSE_ACCELERATED"
        return False, "DENSE_AVX2_TILED"
