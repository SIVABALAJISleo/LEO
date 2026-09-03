"""
hyper_v3/verification/adversarial.py
Adversarial test verification runner checking boundary cases.
"""

from typing import Dict, Any
import numpy as np


class AdversarialVerifier:
    @staticmethod
    def check_boundary_sanity(output: np.ndarray) -> bool:
        if np.isnan(output).any() or np.isinf(output).any():
            return False
        return True
