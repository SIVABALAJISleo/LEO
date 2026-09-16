"""
hyper_x/verification/numerical_verifier.py
==========================================
Phase 1: Numerical Verifier.
Enforces bounded relative and absolute error thresholds according to IEEE 754 precision standards.
Fail-closed default: passed = False.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Tuple
import numpy as np


@dataclass
class NumericalVerificationResult:
    passed: bool = False  # Fail-closed default
    max_absolute_error: float = float("inf")
    relative_error: float = float("inf")
    mean_squared_error: float = float("inf")
    snr_db: float = 0.0


class NumericalVerifier:
    """
    Validates numerical residuals against contract-specified tolerances.
    """

    @classmethod
    def verify(
        cls,
        candidate: np.ndarray,
        reference: np.ndarray,
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-4,
    ) -> NumericalVerificationResult:
        if candidate.shape != reference.shape:
            return NumericalVerificationResult(passed=False)

        c_f64 = candidate.astype(np.float64)
        r_f64 = reference.astype(np.float64)

        abs_diff = np.abs(c_f64 - r_f64)
        max_abs = float(np.max(abs_diff))
        mse = float(np.mean(abs_diff ** 2))

        ref_norm = float(np.linalg.norm(r_f64))
        diff_norm = float(np.linalg.norm(abs_diff))

        rel_err = (diff_norm / ref_norm) if ref_norm > 1e-12 else max_abs

        snr = 10.0 * math.log10(ref_norm**2 / max(1e-12, diff_norm**2)) if diff_norm > 1e-12 else 100.0

        passed = (max_abs <= abs_tolerance) and (rel_err <= rel_tolerance)

        return NumericalVerificationResult(
            passed=passed,
            max_absolute_error=max_abs,
            relative_error=rel_err,
            mean_squared_error=mse,
            snr_db=round(snr, 2),
        )
