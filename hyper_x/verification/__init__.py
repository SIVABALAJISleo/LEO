"""
hyper_x.verification
====================
Authoritative Fail-Closed Verification Engine.
"""

from .verifier import AuthoritativeVerifier, VerificationStatus
from .numerical import NumericalVerifier
from .adversarial import AdversarialVerifier
from .holdout import BlindHoldoutVerifier

__all__ = [
    "AuthoritativeVerifier",
    "VerificationStatus",
    "NumericalVerifier",
    "AdversarialVerifier",
    "BlindHoldoutVerifier",
]
