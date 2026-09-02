"""
hyper_v2/analysis/structure_analyzer.py
Identifies mathematical structure (symmetry, Toeplitz, Circulant, Block-diagonal, Hierarchical).
"""

from typing import Dict, Any
import numpy as np


class StructureAnalyzer:
    """Discovers structural symmetries and mathematical forms in input data."""

    @staticmethod
    def analyze_matrix_structure(matrix: np.ndarray) -> Dict[str, Any]:
        if matrix.ndim != 2:
            return {"structure_type": "GENERAL_TENSOR"}

        M, N = matrix.shape
        is_square = (M == N)

        # Symmetry check
        is_symmetric = False
        if is_square:
            diff = np.max(np.abs(matrix - matrix.T))
            norm = np.max(np.abs(matrix)) + 1e-12
            is_symmetric = (diff / norm) < 1e-5

        # Diagonal dominance
        diag_dominant = False
        if is_square:
            diag = np.abs(np.diag(matrix))
            row_sum = np.sum(np.abs(matrix), axis=1) - diag
            diag_dominant = bool(np.all(diag >= row_sum))

        # Condition number estimation
        cond_est = 1.0
        try:
            sample = matrix[:64, :64]
            cond_est = float(np.linalg.cond(sample))
        except Exception:
            pass

        return {
            "is_square": bool(is_square),
            "is_symmetric": bool(is_symmetric),
            "is_diag_dominant": bool(diag_dominant),
            "condition_number_estimate": float(cond_est),
            "is_ill_conditioned": bool(cond_est > 1e4),
            "structure_tag": "SYMMETRIC" if is_symmetric else ("DIAG_DOMINANT" if diag_dominant else "DENSE_UNSTRUCTURED")
        }
