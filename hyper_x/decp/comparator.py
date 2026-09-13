#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/decp/comparator.py
==========================
Phase 7: Cross-Hardware Comparator & ULP Distribution Analyzer.
"""

import hashlib
from typing import Dict, Any, Tuple
import numpy as np


class CrossHardwareComparator:
    """Compares candidate and reference outputs for bit-exactness and numerical parity."""

    @staticmethod
    def compute_sha256(array: np.ndarray) -> str:
        arr_contiguous = np.ascontiguousarray(array)
        return hashlib.sha256(arr_contiguous.tobytes()).hexdigest()

    @staticmethod
    def calculate_ulp_distance(cand: np.ndarray, ref: np.ndarray) -> float:
        """Calculates mean Units in the Last Place (ULP) distance for floating point."""
        c = np.asarray(cand, dtype=np.float32)
        r = np.asarray(ref, dtype=np.float32)
        eps = np.finfo(np.float32).eps
        diff = np.abs(c - r)
        ulp = diff / (eps * (np.abs(r) + 1e-12))
        return float(np.mean(ulp))

    @staticmethod
    def compare(
        cand_out: np.ndarray,
        ref_out: np.ndarray,
        rel_tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        cand = np.asarray(cand_out, dtype=np.float32)
        ref = np.asarray(ref_out, dtype=np.float32)

        cand_hash = CrossHardwareComparator.compute_sha256(cand)
        ref_hash = CrossHardwareComparator.compute_sha256(ref)

        bit_exact = (cand_hash == ref_hash)
        elementwise_equal = bool(np.array_equal(cand, ref))

        ref_norm = float(np.linalg.norm(ref))
        diff_norm = float(np.linalg.norm(cand - ref))
        rel_err = float(diff_norm / max(ref_norm, 1e-12))
        max_abs = float(np.max(np.abs(cand - ref)))
        mean_ulp = CrossHardwareComparator.calculate_ulp_distance(cand, ref)

        if bit_exact or elementwise_equal:
            classification = "EXACT_MATCH"
            bit_exact_parity = 100.0
            exact_comp_parity = 100.0
            contract_parity = 100.0
        elif rel_err <= rel_tolerance:
            classification = "NUMERIC_MATCH"
            bit_exact_parity = 0.0
            exact_comp_parity = 0.0
            contract_parity = 100.0
        elif rel_err <= 0.05:
            classification = "CONTRACT_MATCH"
            bit_exact_parity = 0.0
            exact_comp_parity = 0.0
            contract_parity = 95.0
        else:
            classification = "MISMATCH"
            bit_exact_parity = 0.0
            exact_comp_parity = 0.0
            contract_parity = 0.0

        return {
            "classification": classification,
            "bit_exact_output_parity_pct": bit_exact_parity,
            "exact_computational_parity_pct": exact_comp_parity,
            "contract_parity_pct": contract_parity,
            "candidate_output_sha256": cand_hash,
            "reference_output_sha256": ref_hash,
            "relative_error": rel_err,
            "max_abs_error": max_abs,
            "mean_ulp_distance": round(mean_ulp, 2)
        }
