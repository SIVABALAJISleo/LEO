#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/numerical.py
=================================
Phase 6: Rigorous Numerical Verification.
Calculates Frobenius relative error, absolute error, RMS error, and detects NaN/Inf anomalies.
"""

from typing import Dict, Any, Tuple
import numpy as np


class NumericalVerifier:
    """Evaluates numerical outputs against declared mathematical contracts."""

    @staticmethod
    def evaluate(
        candidate_out: np.ndarray,
        reference_out: np.ndarray,
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-5
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates numerical accuracy.
        Fail-closed: Returns (passed, metrics).
        """
        cand = np.asarray(candidate_out)
        ref = np.asarray(reference_out)

        # 1. NaN / Inf anomaly check
        if np.isnan(cand).any() or np.isinf(cand).any():
            return False, {
                "passed": False,
                "failure_reason": "Candidate output contains NaN or Inf values",
                "rel_error": float("inf"),
                "abs_error": float("inf")
            }

        # 2. Shape compatibility check
        if cand.shape != ref.shape:
            return False, {
                "passed": False,
                "failure_reason": f"Shape mismatch: {cand.shape} vs {ref.shape}",
                "rel_error": float("inf"),
                "abs_error": float("inf")
            }

        # 3. Maximum Absolute Error
        abs_diff = np.abs(cand - ref)
        max_abs_err = float(np.max(abs_diff))

        # 4. Relative Frobenius Norm Error
        ref_norm = float(np.linalg.norm(ref))
        diff_norm = float(np.linalg.norm(cand - ref))
        rel_err = float(diff_norm / max(ref_norm, 1e-12))

        # 5. Root Mean Squared Error (RMSE)
        rmse = float(np.sqrt(np.mean(abs_diff ** 2)))

        # Fail-closed tolerance checks
        abs_ok = (max_abs_err <= abs_tolerance)
        rel_ok = (rel_err <= rel_tolerance)
        passed = (rel_ok or abs_ok) if ref_norm < 1e-6 else rel_ok

        failures = []
        if not rel_ok and not (ref_norm < 1e-6 and abs_ok):
            failures.append(f"Relative error {rel_err:.2e} > tolerance {rel_tolerance:.2e}")
        if not abs_ok and ref_norm < 1e-6:
            failures.append(f"Absolute error {max_abs_err:.2e} > tolerance {abs_tolerance:.2e}")

        return passed, {
            "passed": passed,
            "max_abs_error": max_abs_err,
            "relative_error": rel_err,
            "rmse": rmse,
            "rel_tolerance": rel_tolerance,
            "abs_tolerance": abs_tolerance,
            "failures": failures
        }
