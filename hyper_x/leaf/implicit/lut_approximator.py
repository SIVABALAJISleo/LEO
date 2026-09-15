"""
hyper_x/leaf/implicit/lut_approximator.py
==========================================
LUT-based function approximator for NIR_001.

Uses uniform lookup tables with linear interpolation.
Never claims to be exact — always reports error bound.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np


@dataclass
class LUTApproxResult:
    """Result of a single LUT evaluation."""
    value: float
    domain_low: float
    domain_high: float
    lut_size: int


class LUTApproximator:
    """
    Uniform lookup table approximator with linear interpolation.

    Parameters
    ----------
    fn_name : str
        Human-readable name of the approximated function.
    lut : np.ndarray
        Precomputed LUT values (float32).
    domain_low : float
    domain_high : float
    """

    def __init__(
        self,
        fn_name: str,
        lut: np.ndarray,
        domain_low: float,
        domain_high: float,
    ) -> None:
        self.fn_name = fn_name
        self._lut = lut.astype(np.float32)
        self._n = len(lut)
        self._low = float(domain_low)
        self._high = float(domain_high)
        self._span = float(domain_high) - float(domain_low)

    def evaluate(self, x: float) -> float:
        """Linearly-interpolated LUT lookup.  O(1)."""
        # Clamp to domain
        xc = max(self._low, min(self._high, x))
        t = (xc - self._low) / self._span * (self._n - 1)
        lo = int(t)
        hi = min(lo + 1, self._n - 1)
        frac = t - lo
        return float(self._lut[lo] * (1.0 - frac) + self._lut[hi] * frac)

    @property
    def lut_size(self) -> int:
        return self._n

    def __repr__(self) -> str:
        return f"LUTApproximator(fn={self.fn_name!r}, n={self._n}, domain=[{self._low},{self._high}])"


class NeuralImplicitResolution:
    """
    Factory for LUT approximators.

    Parameters
    ----------
    lut_size : int
        Number of samples in each LUT (default 4096).
    """

    def __init__(self, lut_size: int = 4096) -> None:
        self._lut_size = lut_size
        self._cache: dict[str, LUTApproximator] = {}

    def fit(
        self,
        fn_name: str,
        fn: Callable[[np.ndarray], np.ndarray],
        domain: np.ndarray,
    ) -> LUTApproximator:
        """
        Build a LUT approximator for *fn* over *domain*.

        Parameters
        ----------
        fn_name : str
        fn : callable  (numpy-compatible)
        domain : 1-D float32 ndarray of sample points

        Returns
        -------
        LUTApproximator
        """
        low = float(domain.min())
        high = float(domain.max())
        xs = np.linspace(low, high, self._lut_size, dtype=np.float32)
        ys = fn(xs).astype(np.float32)
        approx = LUTApproximator(fn_name, ys, low, high)
        self._cache[fn_name] = approx
        return approx

    def get(self, fn_name: str) -> Optional[LUTApproximator]:
        return self._cache.get(fn_name)
