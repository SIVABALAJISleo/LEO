"""
hyper_v3/proof/numerical.py
Numerical stability analysis, condition number bounding, and catastrophic cancellation detection.
"""

from typing import Dict, Any, Tuple
import numpy as np


class NumericalStabilityAnalyzer:
    """Detects catastrophic cancellation, underflow/overflow, and conditioning risks."""

    @staticmethod
    def check_subtraction_cancellation(a: np.ndarray, b: np.ndarray) -> Dict[str, Any]:
        """Detects catastrophic cancellation when subtracting two nearly equal values."""
        diff = a - b
        nearly_equal = np.abs(a - b) < 1e-4 * np.maximum(np.abs(a), np.abs(b))
        cancellation_ratio = float(np.count_nonzero(nearly_equal) / a.size) if a.size > 0 else 0.0
        return {
            "cancellation_risk": bool(cancellation_ratio > 0.1),
            "cancellation_ratio": cancellation_ratio
        }

    @staticmethod
    def check_dynamic_range(tensor: np.ndarray) -> Dict[str, Any]:
        flat = tensor.ravel()
        if flat.size == 0:
            return {"dynamic_range_db": 0.0}
        pos_vals = np.abs(flat[flat != 0])
        if pos_vals.size == 0:
            return {"dynamic_range_db": 0.0}
        min_v = float(np.min(pos_vals))
        max_v = float(np.max(pos_vals))
        ratio = max_v / max(min_v, 1e-38)
        dr_db = float(20.0 * np.log10(ratio))
        return {
            "min_positive": min_v,
            "max_value": max_v,
            "dynamic_range_db": dr_db,
            "overflow_risk": bool(max_v > 1e30),
            "underflow_risk": bool(min_v < 1e-30)
        }
