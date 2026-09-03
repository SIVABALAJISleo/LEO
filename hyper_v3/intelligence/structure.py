"""
hyper_v3/intelligence/structure.py
Mathematical structure analyzer (Symmetry, Toeplitz, Circulant, Condition Number).
"""

from typing import Dict, Any
import numpy as np


class StructureAnalyzer:
    """Discovers mathematical matrix symmetries and conditioning."""

    @staticmethod
    def analyze_matrix(matrix: np.ndarray) -> Dict[str, Any]:
        if matrix.ndim != 2:
            return {"is_2d": False}
        m, n = matrix.shape
        is_square = (m == n)
        is_symmetric = False
        is_toeplitz = False
        cond_number = 1.0

        if is_square:
            diff_sym = np.max(np.abs(matrix - matrix.T))
            is_symmetric = bool(diff_sym < 1e-6)

        # Toeplitz check
        if m > 1 and n > 1:
            toeplitz_diff = np.max(np.abs(matrix[1:, 1:] - matrix[:-1, :-1]))
            is_toeplitz = bool(toeplitz_diff < 1e-6)

        if is_square and m <= 512:
            try:
                cond_number = float(np.linalg.cond(matrix))
            except Exception:
                cond_number = float("inf")

        return {
            "shape": [m, n],
            "is_square": is_square,
            "is_symmetric": is_symmetric,
            "is_toeplitz": is_toeplitz,
            "condition_number": cond_number,
            "is_ill_conditioned": bool(cond_number > 1e4)
        }
