"""
hyper_x/leaf/implicit/field.py
==============================
Implicit Field Definition for LEAF.

Concept:
    Instead of materializing a large discrete object Y[1...N],
    represent the required observable as a compact mathematical or learned
    function:
        Phi(x; theta)
    where:
        x = query coordinate / input condition
        theta = compact parameters
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class ImplicitField(ABC):
    """Abstract base class for all implicit continuous/discrete fields."""

    @abstractmethod
    def query(self, coordinates: np.ndarray) -> np.ndarray:
        """Evaluates field at specified coordinates. coords shape: (N, D)."""
        pass

    @property
    @abstractmethod
    def parameter_bytes(self) -> int:
        """Returns byte size of compact parameter storage theta."""
        pass


@dataclass
class PolynomialField(ImplicitField):
    """Compact polynomial representation of 1D/2D continuous fields."""
    coefficients: np.ndarray  # Shape: (degree + 1,)
    degree: int

    def query(self, coordinates: np.ndarray) -> np.ndarray:
        coords = np.asarray(coordinates, dtype=np.float32)
        # Horner's method evaluation
        res = np.zeros_like(coords, dtype=np.float32)
        for c in reversed(self.coefficients):
            res = res * coords + c
        return res

    @property
    def parameter_bytes(self) -> int:
        return self.coefficients.nbytes
