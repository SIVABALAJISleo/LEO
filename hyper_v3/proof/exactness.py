"""
hyper_v3/proof/exactness.py
Validates bitwise and numerical exactness between reference and candidate outputs.
"""

from typing import Tuple
import numpy as np


class ExactnessValidator:
    """Validates mathematical and bitwise equality between outputs."""

    @staticmethod
    def check_bitwise_identical(a: np.ndarray, b: np.ndarray) -> bool:
        if a.shape != b.shape or a.dtype != b.dtype:
            return False
        return bool(np.array_equal(a, b))

    @staticmethod
    def measure_errors(reference: np.ndarray, candidate: np.ndarray) -> Tuple[float, float, float]:
        """Returns (max_abs_err, max_rel_err, snr_db)."""
        if reference.shape != candidate.shape:
            return float("inf"), float("inf"), 0.0
        
        ref_f = reference.astype(np.float64)
        cand_f = candidate.astype(np.float64)

        abs_diff = np.abs(ref_f - cand_f)
        max_abs = float(np.max(abs_diff))

        ref_scale = np.maximum(np.abs(ref_f), 1e-12)
        rel_diff = abs_diff / ref_scale
        max_rel = float(np.max(rel_diff))

        signal_pwr = np.mean(ref_f**2)
        noise_pwr = np.mean(abs_diff**2)
        if noise_pwr <= 1e-18:
            snr_db = 150.0
        else:
            snr_db = float(10.0 * np.log10(max(signal_pwr, 1e-18) / noise_pwr))

        return max_abs, max_rel, snr_db
