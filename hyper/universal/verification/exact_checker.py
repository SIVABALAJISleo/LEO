"""
hyper/universal/verification/exact_checker.py
=============================================
Exact Bitwise & Structural Verifier.
Checks identical byte representation, exact integers, and structural equality.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import UniversalVerificationResult, VerificationState, ScientificOutcome
from ..contracts.universal_contract import UniversalContract


class ExactChecker:
    """Verifies bitwise and exact mathematical identity between candidate and reference."""

    @staticmethod
    def verify(
        candidate_output: Any,
        reference_output: Any,
        contract: UniversalContract,
    ) -> UniversalVerificationResult:
        if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
            if candidate_output.shape != reference_output.shape:
                return UniversalVerificationResult(
                    is_valid=False,
                    state=VerificationState.FAILED,
                    scientific_outcome=ScientificOutcome.FAILURE,
                    method_used="EXACT_BITWISE_CHECK",
                    rejection_reason=f"Shape mismatch: {candidate_output.shape} != {reference_output.shape}",
                )

            is_exact = np.array_equal(candidate_output, reference_output)
            if is_exact:
                return UniversalVerificationResult(
                    is_valid=True,
                    state=VerificationState.EXACT_VERIFIED,
                    scientific_outcome=ScientificOutcome.SUCCESS,
                    method_used="EXACT_BITWISE_CHECK",
                    absolute_error=0.0,
                    confidence_score=1.0,
                )
            else:
                max_diff = float(np.max(np.abs(candidate_output - reference_output)))
                return UniversalVerificationResult(
                    is_valid=False,
                    state=VerificationState.FAILED,
                    scientific_outcome=ScientificOutcome.FAILURE,
                    method_used="EXACT_BITWISE_CHECK",
                    absolute_error=max_diff,
                    rejection_reason=f"Exact equality violated (max abs diff = {max_diff:.4e})",
                )

        # Non-array or heterogeneous equality
        try:
            is_exact = bool(np.array_equal(candidate_output, reference_output))
        except Exception:
            is_exact = bool(candidate_output == reference_output)
        return UniversalVerificationResult(
            is_valid=is_exact,
            state=VerificationState.EXACT_VERIFIED if is_exact else VerificationState.FAILED,
            scientific_outcome=ScientificOutcome.SUCCESS if is_exact else ScientificOutcome.FAILURE,
            method_used="EXACT_BITWISE_CHECK",
            rejection_reason=None if is_exact else "Scalar / object equality check failed",
        )
