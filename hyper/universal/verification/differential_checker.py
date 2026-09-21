"""
hyper/universal/verification/differential_checker.py
====================================================
Differential Verifier.
Validates outputs against absolute and relative numerical tolerance bounds.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import UniversalVerificationResult, VerificationState, ScientificOutcome
from ..contracts.universal_contract import UniversalContract


class DifferentialChecker:
    """Verifies numerical fidelity against differential bounds."""

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
                    method_used="DIFFERENTIAL_BOUND_CHECK",
                    rejection_reason=f"Shape mismatch: {candidate_output.shape} != {reference_output.shape}",
                )

            diff = np.abs(candidate_output - reference_output)
            abs_err = float(np.max(diff)) if diff.size > 0 else 0.0

            ref_mag = np.abs(reference_output)
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(ref_mag > 1e-12, diff / ref_mag, diff)
            rel_err = float(np.max(rel)) if rel.size > 0 else 0.0

            tol = contract.numeric_tolerance
            rel_tol = contract.relative_tolerance

            if contract.is_exact():
                is_valid = (abs_err == 0.0)
                state = VerificationState.EXACT_VERIFIED if is_valid else VerificationState.FAILED
            else:
                is_valid = (abs_err <= tol) or (rel_tol > 0 and rel_err <= rel_tol)
                state = VerificationState.NUMERICALLY_VERIFIED if is_valid else VerificationState.FAILED

            reason = None if is_valid else f"Error bounds exceeded: abs={abs_err:.2e} (tol={tol:.2e}), rel={rel_err:.2e} (rel_tol={rel_tol:.2e})"

            return UniversalVerificationResult(
                is_valid=is_valid,
                state=state,
                scientific_outcome=ScientificOutcome.SUCCESS if is_valid else ScientificOutcome.FAILURE,
                method_used="DIFFERENTIAL_BOUND_CHECK",
                absolute_error=abs_err,
                relative_error=rel_err,
                confidence_score=1.0 if is_valid else 0.0,
                rejection_reason=reason,
                details={"abs_err": abs_err, "rel_err": rel_err},
            )

        # Fallback for scalar
        diff = abs(candidate_output - reference_output)
        is_valid = diff <= contract.numeric_tolerance
        return UniversalVerificationResult(
            is_valid=is_valid,
            state=VerificationState.NUMERICALLY_VERIFIED if is_valid else VerificationState.FAILED,
            scientific_outcome=ScientificOutcome.SUCCESS if is_valid else ScientificOutcome.FAILURE,
            method_used="DIFFERENTIAL_BOUND_CHECK",
            absolute_error=float(diff),
            rejection_reason=None if is_valid else f"Scalar diff {diff} exceeded {contract.numeric_tolerance}",
        )
