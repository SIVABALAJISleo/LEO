"""
hyper_x/leaf/verification/numerical.py
======================================
Numerical Distance and Freivalds Probabilistic Verifier for LEAF.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class NumericalVerifier:
    """Rigorous numerical verification suite."""

    def freivalds_verify(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        k_trials: int = 10,
        tolerance: float = 1e-4,
    ) -> Tuple[bool, float]:
        """
        Freivalds algorithm: Verifies A @ B = C in O(k * N^2) instead of O(N^3).
        Tests whether A @ (B @ r) = C @ r for random vector r in {-1, 1}^N.
        Probability of false positive <= 2^-k.
        """
        N = B.shape[1]
        max_diff = 0.0

        for _ in range(k_trials):
            r = np.random.choice([-1.0, 1.0], size=(N, 1)).astype(np.float32)
            Br = np.matmul(B, r)
            ABr = np.matmul(A, Br)
            Cr = np.matmul(C, r)

            diff = np.max(np.abs(ABr - Cr))
            if diff > max_diff:
                max_diff = float(diff)

            if diff > tolerance:
                return False, max_diff

        return True, max_diff

    def relative_frobenius_norm(self, cand: np.ndarray, ref: np.ndarray) -> float:
        denom = np.linalg.norm(ref)
        num = np.linalg.norm(cand - ref)
        if denom > 1e-12:
            return float(num / denom)
        return float(np.max(np.abs(cand - ref)))
