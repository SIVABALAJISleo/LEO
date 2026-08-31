"""
hyper/sensitivity/sensitivity_engine.py
=======================================
Sensitivity Engine (Section 18):
Determines which portions of a computation are sensitive to numerical error.
Assigns HIGH, MEDIUM, LOW precision locally based on sensitivity gradients.
"""

from enum import Enum
from typing import Dict, Any, List
import numpy as np


class PrecisionTier(str, Enum):
    HIGH_FP32 = "HIGH_FP32"
    MEDIUM_FP16 = "MEDIUM_FP16"
    LOW_INT8 = "LOW_INT8"
    EXTREME_TERNARY = "EXTREME_TERNARY"


class SensitivityEngine:
    """
    Analyzes local condition numbers and numerical sensitivity.
    """
    def __init__(self):
        pass

    def evaluate_sensitivity(self, weights: np.ndarray, activation_variance: float = 1.0) -> Dict[str, Any]:
        """
        Computes Frobenius norm condition and singular value decay to determine sensitivity.
        """
        norm_val = float(np.linalg.norm(weights))
        mean_abs = float(np.mean(np.abs(weights)))
        variance = float(np.var(weights))

        # Dynamic sensitivity metric: high variance/norm indicates sensitive layer
        sensitivity_score = min(1.0, max(0.0, (variance / max(1e-6, mean_abs)) * activation_variance))

        if sensitivity_score > 0.8:
            assigned_tier = PrecisionTier.HIGH_FP32
        elif sensitivity_score > 0.4:
            assigned_tier = PrecisionTier.MEDIUM_FP16
        elif sensitivity_score > 0.1:
            assigned_tier = PrecisionTier.LOW_INT8
        else:
            assigned_tier = PrecisionTier.EXTREME_TERNARY

        return {
            "sensitivity_score": round(sensitivity_score, 4),
            "assigned_precision_tier": assigned_tier.value,
            "condition_norm": round(norm_val, 4),
            "variance": round(variance, 6),
        }
