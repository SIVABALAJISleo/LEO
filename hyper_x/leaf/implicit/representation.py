"""
hyper_x/leaf/implicit/representation.py
=======================================
Compact mathematical representation models for LEAF.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .field import ImplicitField


@dataclass
class FourierFeatureField(ImplicitField):
    """
    Compact Fourier basis expansion representation:
    Phi(x) = sum_k a_k cos(w_k x) + b_k sin(w_k x)
    """
    frequencies: np.ndarray      # (K,)
    cos_coeffs: np.ndarray       # (K,)
    sin_coeffs: np.ndarray       # (K,)
    bias: float = 0.0

    def query(self, coordinates: np.ndarray) -> np.ndarray:
        coords = np.asarray(coordinates, dtype=np.float32).ravel()
        # Shape: (N, K)
        phases = coords[:, np.newaxis] * self.frequencies[np.newaxis, :]
        val = np.sum(
            self.cos_coeffs * np.cos(phases) + self.sin_coeffs * np.sin(phases),
            axis=1,
        ) + self.bias
        return val.reshape(coordinates.shape)

    @property
    def parameter_bytes(self) -> int:
        return self.frequencies.nbytes + self.cos_coeffs.nbytes + self.sin_coeffs.nbytes + 4


@dataclass
class LowRankImplicitMatrix(ImplicitField):
    """
    Low-rank factorized implicit field:
    M(i, j) = U[i, :] @ V[j, :]^T
    """
    U: np.ndarray  # (M, R)
    V: np.ndarray  # (N, R)
    rank: int

    def query(self, coordinates: np.ndarray) -> np.ndarray:
        """Query coordinate pairs (i, j)."""
        coords = np.asarray(coordinates, dtype=np.int64)
        if coords.ndim == 1:
            i, j = coords[0], coords[1]
            return np.dot(self.U[i], self.V[j])
        elif coords.ndim == 2:
            i_idx = coords[:, 0]
            j_idx = coords[:, 1]
            return np.sum(self.U[i_idx] * self.V[j_idx], axis=1)
        raise ValueError(f"Invalid coordinate dimensions: {coords.shape}")

    def materialize_full(self) -> np.ndarray:
        return np.matmul(self.U, self.V.T)

    @property
    def parameter_bytes(self) -> int:
        return self.U.nbytes + self.V.nbytes
