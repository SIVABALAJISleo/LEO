"""
hyper/universal/verification/freivalds.py
========================================
Freivalds Algorithm for Randomized Matrix Multiplication Verification.
Checks A @ B = C in O(k N^2) time vs O(N^3) standard evaluation.
Error probability <= 2^(-k). For k=20, failure probability is < 10^-6.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import UniversalVerificationResult, VerificationState, ScientificOutcome
from ..contracts.universal_contract import UniversalContract


class FreivaldsVerifier:
    """Randomized O(k N^2) matrix multiplication verifier."""

    @staticmethod
    def verify(
        A: np.ndarray,
        B: np.ndarray,
        C_candidate: np.ndarray,
        k: int = 15,
        tolerance: float = 1e-4,
    ) -> UniversalVerificationResult:
        if A.shape[1] != B.shape[0] or A.shape[0] != C_candidate.shape[0] or B.shape[1] != C_candidate.shape[1]:
            return UniversalVerificationResult(
                is_valid=False,
                state=VerificationState.FAILED,
                scientific_outcome=ScientificOutcome.FAILURE,
                method_used="FREIVALDS_O(k*N^2)_ALGORITHM",
                rejection_reason="Matrix dimension mismatch for A @ B == C",
            )

        n = B.shape[1]
        rng = np.random.default_rng(42)

        for trial in range(k):
            # Random vector r in {0, 1}^n
            r = rng.integers(0, 2, size=(n, 1)).astype(np.float32)

            # Check A @ (B @ r) - C @ r == 0
            Br = B @ r
            ABr = A @ Br
            Cr = C_candidate @ r

            diff = np.max(np.abs(ABr - Cr))
            if diff > tolerance:
                return UniversalVerificationResult(
                    is_valid=False,
                    state=VerificationState.FAILED,
                    scientific_outcome=ScientificOutcome.FAILURE,
                    method_used="FREIVALDS_O(k*N^2)_ALGORITHM",
                    absolute_error=float(diff),
                    rejection_reason=f"Freivalds check failed on trial {trial+1}/{k} (diff={diff:.4e} > tol={tolerance})",
                )

        confidence = 1.0 - (0.5 ** k)
        return UniversalVerificationResult(
            is_valid=True,
            state=VerificationState.NUMERICALLY_VERIFIED if tolerance > 0 else VerificationState.EXACT_VERIFIED,
            scientific_outcome=ScientificOutcome.SUCCESS,
            method_used="FREIVALDS_O(k*N^2)_ALGORITHM",
            confidence_score=confidence,
            details={"trials_k": k, "theoretical_error_prob": 0.5 ** k},
        )
