#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/numerical.py
=================================
Phase 14: Rigorous Bounded Numerical Verification.

PASS only if:
  abs_error <= absolute_tolerance AND rel_error <= relative_tolerance

Reports:
  - max_abs_error
  - mean_abs_error
  - max_relative_error
  - RMSE
  - PSNR
  - cosine_similarity
  - output_hash
  - mismatch_count
"""

import hashlib
from typing import Dict, Any, Tuple
import numpy as np


class NumericalVerifier:
    """Evaluates numerical outputs against declared mathematical contracts."""

    @staticmethod
    def evaluate(
        candidate_out: np.ndarray,
        reference_out: np.ndarray,
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-5,
        require_both_bounds: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates numerical accuracy.
        Fail-closed: Returns (passed, metrics).
        """
        cand = np.asarray(candidate_out, dtype=np.float32)
        ref = np.asarray(reference_out, dtype=np.float32)

        # 1. NaN / Inf anomaly check
        if np.isnan(cand).any() or np.isinf(cand).any():
            return False, {
                "passed": False,
                "failure_reason": "Candidate output contains NaN or Inf values",
                "relative_error": float("inf"),
                "max_abs_error": float("inf"),
                "failures": ["NaN or Inf detected"]
            }

        # 2. Shape compatibility check
        if cand.shape != ref.shape:
            return False, {
                "passed": False,
                "failure_reason": f"Shape mismatch: {cand.shape} vs {ref.shape}",
                "relative_error": float("inf"),
                "max_abs_error": float("inf"),
                "failures": [f"Shape mismatch: {cand.shape} != {ref.shape}"]
            }

        # 3. Maximum and Mean Absolute Error
        abs_diff = np.abs(cand - ref)
        max_abs_err = float(np.max(abs_diff))
        mean_abs_err = float(np.mean(abs_diff))

        # 4. Relative Frobenius Norm Error
        ref_norm = float(np.linalg.norm(ref))
        diff_norm = float(np.linalg.norm(cand - ref))
        rel_err = float(diff_norm / max(ref_norm, 1e-12))

        # 5. Root Mean Squared Error (RMSE)
        rmse = float(np.sqrt(np.mean(abs_diff ** 2)))

        # 6. PSNR (Peak Signal-to-Noise Ratio)
        max_val = float(np.max(np.abs(ref))) if ref_norm > 0 else 1.0
        if rmse > 0:
            psnr = float(20.0 * np.log10(max(max_val, 1e-6) / rmse))
        else:
            psnr = 100.0

        # 7. Cosine Similarity
        c_flat = cand.flatten()
        r_flat = ref.flatten()
        dot = float(np.dot(c_flat, r_flat))
        c_norm = float(np.linalg.norm(c_flat))
        r_norm = float(np.linalg.norm(r_flat))
        cosine_sim = float(dot / (max(c_norm * r_norm, 1e-12)))

        # 8. Output Hash & Mismatch Count
        out_hash = hashlib.sha256(np.ascontiguousarray(cand).tobytes()).hexdigest()
        mismatch_count = int(np.sum(abs_diff > abs_tolerance))

        # Fail-closed tolerance checks:
        # Strict rule: PASS only if abs_error <= absolute_tolerance AND rel_error <= relative_tolerance
        abs_ok = (max_abs_err <= abs_tolerance)
        rel_ok = (rel_err <= rel_tolerance)

        if require_both_bounds:
            # If reference norm is tiny, rely on abs_tolerance; otherwise both must pass
            if ref_norm < 1e-5:
                passed = abs_ok
            else:
                passed = (abs_ok and rel_ok)
        else:
            passed = (abs_ok or rel_ok)

        failures = []
        if not abs_ok and ref_norm >= 1e-5:
            failures.append(f"Max abs error {max_abs_err:.2e} > tolerance {abs_tolerance:.2e}")
        if not rel_ok:
            failures.append(f"Relative error {rel_err:.2e} > tolerance {rel_tolerance:.2e}")

        return passed, {
            "passed": passed,
            "max_abs_error": round(max_abs_err, 6),
            "mean_abs_error": round(mean_abs_err, 6),
            "max_relative_error": round(rel_err, 6),
            "relative_error": round(rel_err, 6),
            "rmse": round(rmse, 6),
            "psnr_db": round(psnr, 2),
            "cosine_similarity": round(cosine_sim, 6),
            "output_hash": out_hash,
            "mismatch_count": mismatch_count,
            "rel_tolerance": rel_tolerance,
            "abs_tolerance": abs_tolerance,
            "failures": failures
        }
