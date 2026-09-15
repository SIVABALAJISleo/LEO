"""
hyper_x/leaf/implicit/encoder.py
================================
Encodes discrete grids or matrices into compact implicit representations.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .field import ImplicitField, PolynomialField
from .representation import FourierFeatureField, LowRankImplicitMatrix


class ImplicitEncoder:
    """Encodes discrete arrays into compact continuous or factorized fields."""

    def fit_polynomial(self, x: np.ndarray, y: np.ndarray, degree: int = 5) -> PolynomialField:
        """Fits a 1D polynomial to coordinate-value pairs."""
        coeffs = np.polyfit(x, y, deg=degree).astype(np.float32)
        # polyfit returns highest power first; reverse so c[0] is constant
        coeffs_asc = coeffs[::-1]
        return PolynomialField(coefficients=coeffs_asc, degree=degree)

    def fit_low_rank(self, matrix: np.ndarray, rank: int = 16) -> LowRankImplicitMatrix:
        """Fits SVD low-rank factorized implicit field."""
        u, s, vt = np.linalg.svd(matrix, full_matrices=False)
        r = min(rank, len(s))
        U_r = (u[:, :r] * np.sqrt(s[:r])).astype(np.float32)
        V_r = (vt[:r, :].T * np.sqrt(s[:r])).astype(np.float32)
        return LowRankImplicitMatrix(U=U_r, V=V_r, rank=r)
