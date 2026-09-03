"""
hyper_v3/verification/differential.py
Differential verification checking across multiple backends (NumPy vs SciPy vs PyTorch).
"""

from typing import Dict, Any, Tuple
import numpy as np


class DifferentialVerifier:
    @staticmethod
    def compare_differential(reference: np.ndarray, candidate: np.ndarray) -> Tuple[bool, float]:
        diff = np.max(np.abs(reference - candidate))
        scale = np.max(np.abs(reference)) + 1e-12
        rel_diff = float(diff / scale)
        return (rel_diff < 1e-4), rel_diff
