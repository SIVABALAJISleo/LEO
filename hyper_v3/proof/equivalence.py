"""
hyper_v3/proof/equivalence.py
Algebraic, graph-level, and mathematical equivalence verifier.
"""

from typing import Dict, Any, List
import numpy as np


class EquivalenceChecker:
    """Verifies algebraic equivalence of transformed expressions."""

    @staticmethod
    def verify_distributive_identity(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """Verifies A*(B + C) == A*B + A*C."""
        left = a @ (b + c)
        right = a @ b + a @ c
        max_diff = float(np.max(np.abs(left - right)))
        scale = float(np.max(np.abs(left))) + 1e-12
        return (max_diff / scale) < 1e-5

    @staticmethod
    def verify_associative_identity(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """Verifies (A*B)*C == A*(B*C) within FP numerical precision."""
        left = (a @ b) @ c
        right = a @ (b @ c)
        max_diff = float(np.max(np.abs(left - right)))
        scale = float(np.max(np.abs(left))) + 1e-12
        return (max_diff / scale) < 1e-4
