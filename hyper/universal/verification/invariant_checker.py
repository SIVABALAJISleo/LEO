"""
hyper/universal/verification/invariant_checker.py
=================================================
Invariant Verifier.
Validates structural invariants such as monotonicity (sorted arrays),
permutation multiset equality, non-negativity, and conservation laws.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import UniversalVerificationResult, VerificationState, ScientificOutcome
from ..contracts.universal_contract import UniversalContract


class InvariantChecker:
    """Verifies mathematical and domain-specific invariants."""

    @staticmethod
    def verify_sorted_monotonic(arr: np.ndarray) -> UniversalVerificationResult:
        """Verifies that an array is non-decreasing monotonic."""
        if not isinstance(arr, np.ndarray) or arr.size <= 1:
            return UniversalVerificationResult(
                is_valid=True,
                state=VerificationState.INVARIANT_VERIFIED,
                scientific_outcome=ScientificOutcome.SUCCESS,
                method_used="INVARIANT_MONOTONIC_SORTED",
            )

        diffs = np.diff(arr)
        is_sorted = bool(np.all(diffs >= 0))

        if is_sorted:
            return UniversalVerificationResult(
                is_valid=True,
                state=VerificationState.INVARIANT_VERIFIED,
                scientific_outcome=ScientificOutcome.SUCCESS,
                method_used="INVARIANT_MONOTONIC_SORTED",
                confidence_score=1.0,
            )
        else:
            inversion_count = int(np.count_nonzero(diffs < 0))
            return UniversalVerificationResult(
                is_valid=False,
                state=VerificationState.FAILED,
                scientific_outcome=ScientificOutcome.FAILURE,
                method_used="INVARIANT_MONOTONIC_SORTED",
                rejection_reason=f"Monotonic sorted invariant violated ({inversion_count} inversions detected)",
            )

    @staticmethod
    def verify_permutation(arr1: np.ndarray, arr2: np.ndarray) -> UniversalVerificationResult:
        """Verifies that arr1 is a valid permutation of arr2 (identical multiset)."""
        if arr1.shape != arr2.shape:
            return UniversalVerificationResult(
                is_valid=False,
                state=VerificationState.FAILED,
                scientific_outcome=ScientificOutcome.FAILURE,
                method_used="INVARIANT_PERMUTATION_MULTISET",
                rejection_reason="Shape mismatch in permutation check",
            )

        u1, c1 = np.unique(arr1, return_counts=True)
        u2, c2 = np.unique(arr2, return_counts=True)

        is_perm = np.array_equal(u1, u2) and np.array_equal(c1, c2)
        return UniversalVerificationResult(
            is_valid=is_perm,
            state=VerificationState.INVARIANT_VERIFIED if is_perm else VerificationState.FAILED,
            scientific_outcome=ScientificOutcome.SUCCESS if is_perm else ScientificOutcome.FAILURE,
            method_used="INVARIANT_PERMUTATION_MULTISET",
            rejection_reason=None if is_perm else "Multiset elements or frequencies differ",
        )
