"""
hyper/core/verification/__init__.py
Differential verification and adversarial counterexample generation.
"""
from hyper.core.verification.verifier import (
    AdversarialCounterexampleHunter,
    IndependentVerifier,
    VerificationResult,
)

__all__ = [
    "AdversarialCounterexampleHunter",
    "IndependentVerifier",
    "VerificationResult",
]
