"""
hyper/escape_engine/verification/invariant_verifier.py
======================================================
VAEE Invariant Verifier.
Checks domain-specific mathematical invariants that must hold regardless of algorithm formulation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import numpy as np

from .schema import VerificationOutcome, VerificationTrustLevel


class InvariantVerifier:
    """Verifies mathematical invariants without needing the reference answer."""

    @staticmethod
    def verify_sorting_invariant(arr: Any) -> VerificationOutcome:
        """Verifies sequence is monotonically non-decreasing."""
        if isinstance(arr, np.ndarray):
            if arr.size <= 1:
                return VerificationOutcome(is_valid=True, trust_level=VerificationTrustLevel.INVARIANT_VERIFIED, method="INVARIANT_SORTED")
            is_sorted = bool(np.all(arr[:-1] <= arr[1:]))
        elif isinstance(arr, (list, tuple)):
            if len(arr) <= 1:
                return VerificationOutcome(is_valid=True, trust_level=VerificationTrustLevel.INVARIANT_VERIFIED, method="INVARIANT_SORTED")
            is_sorted = all(arr[i] <= arr[i+1] for i in range(len(arr)-1))
        else:
            is_sorted = False

        return VerificationOutcome(
            is_valid=is_sorted,
            trust_level=VerificationTrustLevel.INVARIANT_VERIFIED if is_sorted else VerificationTrustLevel.FAILED,
            method="INVARIANT_SORTED",
            invariant_passed=is_sorted,
            rejection_reason=None if is_sorted else "Output sequence violated monotonicity invariant (not sorted)",
        )

    @staticmethod
    def verify_symmetry_invariant(mat: np.ndarray) -> VerificationOutcome:
        """Verifies output matrix preserves symmetry A == A.T."""
        if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
            return VerificationOutcome(is_valid=False, trust_level=VerificationTrustLevel.FAILED, method="INVARIANT_SYMMETRY", rejection_reason="Non-square matrix")
        is_sym = bool(np.allclose(mat, mat.T, atol=1e-5))
        return VerificationOutcome(
            is_valid=is_sym,
            trust_level=VerificationTrustLevel.INVARIANT_VERIFIED if is_sym else VerificationTrustLevel.FAILED,
            method="INVARIANT_SYMMETRY",
            invariant_passed=is_sym,
            rejection_reason=None if is_sym else "Output violated symmetry invariant",
        )

    @staticmethod
    def verify_conservation_invariant(candidate: np.ndarray, reference: np.ndarray, tolerance: float = 1e-4) -> VerificationOutcome:
        """Verifies integral or total mass/energy sum is conserved: sum(candidate) == sum(reference)."""
        c_sum = float(np.sum(candidate))
        r_sum = float(np.sum(reference))
        diff = abs(c_sum - r_sum)
        passed = diff <= tolerance
        return VerificationOutcome(
            is_valid=passed,
            trust_level=VerificationTrustLevel.INVARIANT_VERIFIED if passed else VerificationTrustLevel.FAILED,
            method="INVARIANT_CONSERVATION",
            invariant_passed=passed,
            rejection_reason=None if passed else f"Conservation invariant violated: |sum(cand) - sum(ref)| = {diff:.2e} > {tolerance:.2e}",
        )
