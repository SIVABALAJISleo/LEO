"""
hyper_v3/transforms/algebraic.py
Exact algebraic transformations (Constant folding, Identity elimination, Zero elimination, CSE).
"""

from typing import Dict, Any, Tuple
import numpy as np


class AlgebraicTransformer:
    """Performs exact mathematical algebraic simplifications."""

    @staticmethod
    def eliminate_zeros_in_sparse_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if np.all(a == 0):
            return b
        if np.all(b == 0):
            return a
        return a + b

    @staticmethod
    def fold_constants(a: float, b: float, op: str = "mul") -> float:
        if op == "mul":
            return a * b
        elif op == "add":
            return a + b
        return 0.0

    @staticmethod
    def eliminate_identity_matmul(a: np.ndarray, b: np.ndarray) -> Tuple[bool, np.ndarray]:
        """Checks if either matrix is an Identity matrix I, avoiding O(N^3) computation."""
        if a.ndim == 2 and a.shape[0] == a.shape[1] and np.array_equal(a, np.eye(a.shape[0])):
            return True, b
        if b.ndim == 2 and b.shape[0] == b.shape[1] and np.array_equal(b, np.eye(b.shape[0])):
            return True, a
        return False, a @ b
