"""
hyper/escape_engine/verification/checksum_verifier.py
=====================================================
VAEE Checksum & Probabilistic Matrix Multiplication Verifier (Freivalds Algorithm).

Verifies whether A @ B == C in O(k * N^2) instead of O(N^3) time using Freivalds randomized algorithm:
A @ (B @ r) == C @ r for random vector r in {0, 1}^N.
With k=50 trials, error detection probability is >= 1 - 2^(-50).
"""

from __future__ import annotations

from typing import Tuple
import numpy as np

from .schema import VerificationOutcome, VerificationTrustLevel


class ChecksumVerifier:
    """Probabilistic and state checksum verifier."""

    @staticmethod
    def verify_freivalds_gemm(
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        trials: int = 30,
        tolerance: float = 1e-4,
    ) -> VerificationOutcome:
        """
        Verifies A @ B == C probabilistically using Freivalds algorithm.
        A: (M x K), B: (K x N), C: (M x N).
        """
        M, K = A.shape
        K2, N = B.shape
        M2, N2 = C.shape

        if K != K2 or M != M2 or N != N2:
            return VerificationOutcome(
                is_valid=False,
                trust_level=VerificationTrustLevel.FAILED,
                method="FREIVALDS_CHECKSUM",
                rejection_reason="Matrix dimension mismatch",
            )

        rng = np.random.default_rng(42)
        for trial in range(trials):
            # Random boolean vector r in {0, 1}^N
            r = rng.integers(0, 2, size=(N, 1)).astype(np.float32)

            # Compute C @ r
            Cr = C @ r

            # Compute A @ (B @ r) in O(K*N + M*K) operations
            Br = B @ r
            ABr = A @ Br

            diff = np.max(np.abs(ABr - Cr))
            if diff > tolerance:
                return VerificationOutcome(
                    is_valid=False,
                    trust_level=VerificationTrustLevel.FAILED,
                    method="FREIVALDS_CHECKSUM",
                    absolute_error=float(diff),
                    confidence_score=0.0,
                    rejection_reason=f"Freivalds verification failed at trial {trial}: |A(Br) - Cr| = {diff:.2e} > {tolerance:.2e}",
                )

        confidence = 1.0 - (0.5 ** trials)
        return VerificationOutcome(
            is_valid=True,
            trust_level=VerificationTrustLevel.NUMERICALLY_VERIFIED if tolerance > 0 else VerificationTrustLevel.EXACT_VERIFIED,
            method="FREIVALDS_CHECKSUM",
            confidence_score=confidence,
            details={"trials": trials, "error_probability": 0.5 ** trials},
        )
