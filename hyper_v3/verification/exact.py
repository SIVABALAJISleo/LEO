"""
hyper_v3/verification/exact.py
Exact verification routines for bitwise identical assertions.
"""

import numpy as np


class ExactVerifier:
    @staticmethod
    def verify(a: np.ndarray, b: np.ndarray) -> bool:
        return bool(np.array_equal(a, b))
