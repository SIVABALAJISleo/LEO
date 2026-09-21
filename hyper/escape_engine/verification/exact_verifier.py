"""
hyper/escape_engine/verification/exact_verifier.py
==================================================
VAEE Exact Bitwise & Structural Verifier.
Checks identical equality (0 error) for discrete algorithms, permutations, and integer outputs.
"""

from __future__ import annotations

from typing import Any, Tuple
import numpy as np

from .schema import VerificationOutcome, VerificationTrustLevel


class ExactVerifier:
    """Verifies 100% bitwise or integer exactness."""

    @staticmethod
    def verify(candidate_output: Any, reference_output: Any) -> VerificationOutcome:
        if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
            if candidate_output.shape != reference_output.shape:
                return VerificationOutcome(
                    is_valid=False,
                    trust_level=VerificationTrustLevel.FAILED,
                    method="EXACT_COMPARISON",
                    rejection_reason=f"Shape mismatch: {candidate_output.shape} vs {reference_output.shape}",
                )
            is_equal = bool(np.array_equal(candidate_output, reference_output))
            diff = np.max(np.abs(candidate_output - reference_output)) if candidate_output.size > 0 else 0.0
            return VerificationOutcome(
                is_valid=is_equal,
                trust_level=VerificationTrustLevel.EXACT_VERIFIED if is_equal else VerificationTrustLevel.FAILED,
                method="EXACT_COMPARISON",
                absolute_error=float(diff),
                relative_error=0.0 if is_equal else 1.0,
                confidence_score=1.0 if is_equal else 0.0,
                rejection_reason=None if is_equal else f"Exact match failed; max diff: {diff}",
            )

        is_equal = candidate_output == reference_output
        return VerificationOutcome(
            is_valid=bool(is_equal),
            trust_level=VerificationTrustLevel.EXACT_VERIFIED if is_equal else VerificationTrustLevel.FAILED,
            method="EXACT_COMPARISON",
            confidence_score=1.0 if is_equal else 0.0,
            rejection_reason=None if is_equal else "Values are not strictly identical",
        )
