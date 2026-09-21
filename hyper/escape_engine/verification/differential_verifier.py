"""
hyper/escape_engine/verification/differential_verifier.py
=========================================================
VAEE Differential Verifier.
Compares candidate output against a trusted reference under strict absolute/relative bounds.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import VerificationOutcome, VerificationTrustLevel
from ..contracts.schema import ComputationalContract


class DifferentialVerifier:
    """Verifies numerical fidelity against trusted reference implementation."""

    @staticmethod
    def verify(
        candidate_output: Any,
        reference_output: Any,
        contract: ComputationalContract,
    ) -> VerificationOutcome:
        if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
            if candidate_output.shape != reference_output.shape:
                return VerificationOutcome(
                    is_valid=False,
                    trust_level=VerificationTrustLevel.FAILED,
                    method="DIFFERENTIAL_VERIFICATION",
                    rejection_reason=f"Shape mismatch: {candidate_output.shape} vs {reference_output.shape}",
                )

            diff = np.abs(candidate_output - reference_output)
            abs_err = float(np.max(diff)) if diff.size > 0 else 0.0

            ref_mag = np.abs(reference_output)
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(ref_mag > 0, diff / ref_mag, diff)
            rel_err = float(np.max(rel)) if rel.size > 0 else 0.0

            tol = contract.numeric_tolerance
            rel_tol = contract.relative_tolerance

            # Check exact or numerical satisfaction
            if tol == 0.0 and rel_tol == 0.0:
                is_valid = abs_err == 0.0
                trust = VerificationTrustLevel.EXACT_VERIFIED if is_valid else VerificationTrustLevel.FAILED
            else:
                is_valid = (abs_err <= tol) or (rel_tol > 0 and rel_err <= rel_tol)
                trust = VerificationTrustLevel.NUMERICALLY_VERIFIED if is_valid else VerificationTrustLevel.FAILED

            reason = None if is_valid else f"Error bounds exceeded: abs={abs_err:.2e} (tol={tol:.2e}), rel={rel_err:.2e} (rel_tol={rel_tol:.2e})"

            return VerificationOutcome(
                is_valid=is_valid,
                trust_level=trust,
                method="DIFFERENTIAL_VERIFICATION",
                absolute_error=abs_err,
                relative_error=rel_err,
                confidence_score=1.0 if is_valid else 0.0,
                rejection_reason=reason,
                details={"abs_err": abs_err, "rel_err": rel_err, "max_allowed_abs": tol, "max_allowed_rel": rel_tol},
            )

        # Fallback for scalar/general outputs
        is_valid = candidate_output == reference_output
        return VerificationOutcome(
            is_valid=is_valid,
            trust_level=VerificationTrustLevel.EXACT_VERIFIED if is_valid else VerificationTrustLevel.FAILED,
            method="DIFFERENTIAL_VERIFICATION",
            rejection_reason=None if is_valid else "Outputs did not match",
        )
