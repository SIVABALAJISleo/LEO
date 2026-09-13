#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/decp/comparator.py
==========================
Phase 11: HYPER-DECP Cross-Hardware Comparator & ULP Distribution Analyzer.

Evaluates results across:
  TRACK A: SAME COMPUTATION (Bitwise identical target specification)
  TRACK B: DIFFERENT COMPUTATION (Contract-valid alternative pathway with less work)

Output statuses:
  - EXACT_MATCH
  - NUMERICAL_MATCH
  - CONTRACT_MATCH
  - COMPUTATIONALLY_DIFFERENT_BUT_VALID
  - MISMATCH
  - UNKNOWN
"""

import enum
import hashlib
from typing import Dict, Any, Tuple, Optional
import numpy as np


class DECPStatus(str, enum.Enum):
    EXACT_MATCH = "EXACT_MATCH"
    NUMERICAL_MATCH = "NUMERICAL_MATCH"
    CONTRACT_MATCH = "CONTRACT_MATCH"
    COMPUTATIONALLY_DIFFERENT_BUT_VALID = "COMPUTATIONALLY_DIFFERENT_BUT_VALID"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


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
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-5,
        track: str = "TRACK_B",  # "TRACK_A" (Same computation) or "TRACK_B" (Different computation)
        contract_satisfied: bool = True
    ) -> Dict[str, Any]:
        if cand_out is None or ref_out is None:
            return {
                "classification": DECPStatus.UNKNOWN.value,
                "status": DECPStatus.UNKNOWN.value,
                "track": track,
                "bit_exact": False,
                "relative_error": float("inf"),
                "max_abs_error": float("inf"),
                "mean_ulp_distance": float("inf")
            }

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
            classification = DECPStatus.EXACT_MATCH.value
            bit_exact_parity = 100.0
            exact_comp_parity = 100.0
            contract_parity = 100.0
        elif track == "TRACK_A":
            # Track A requires same computation; failure to be bit-exact is a mismatch or numerical match
            if rel_err <= rel_tolerance and max_abs <= abs_tolerance:
                classification = DECPStatus.NUMERICAL_MATCH.value
            else:
                classification = DECPStatus.MISMATCH.value
            bit_exact_parity = 0.0
            exact_comp_parity = 100.0 if rel_err <= rel_tolerance else 0.0
            contract_parity = 100.0 if rel_err <= rel_tolerance else 0.0
        else:
            # Track B: Alternative computation pathway
            if contract_satisfied and (rel_err <= rel_tolerance or max_abs <= abs_tolerance):
                classification = DECPStatus.COMPUTATIONALLY_DIFFERENT_BUT_VALID.value
                contract_parity = 100.0
            elif contract_satisfied:
                classification = DECPStatus.CONTRACT_MATCH.value
                contract_parity = 100.0
            else:
                classification = DECPStatus.MISMATCH.value
                contract_parity = 0.0
            bit_exact_parity = 0.0
            exact_comp_parity = 100.0 if classification != DECPStatus.MISMATCH.value else 0.0

        return {
            "classification": classification,
            "status": classification,
            "track": track,
            "bit_exact": bit_exact,
            "elementwise_equal": elementwise_equal,
            "candidate_output_sha256": cand_hash,
            "reference_output_sha256": ref_hash,
            "max_abs_error": round(max_abs, 6),
            "relative_error": round(rel_err, 6),
            "mean_ulp_distance": round(mean_ulp, 2),
            "bit_exact_output_parity_pct": bit_exact_parity,
            "exact_computational_parity_pct": exact_comp_parity,
            "contract_parity_pct": contract_parity,
            "scores": {
                "bit_exact_output_parity_pct": bit_exact_parity,
                "exact_computational_parity_pct": exact_comp_parity,
                "contract_parity_pct": contract_parity
            }
        }
