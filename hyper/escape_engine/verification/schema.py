"""
hyper/escape_engine/verification/schema.py
==========================================
VAEE Section 14 & 15: Verification Trust Levels & Results.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional


class VerificationTrustLevel:
    EXACT_VERIFIED = "EXACT_VERIFIED"
    NUMERICALLY_VERIFIED = "NUMERICALLY_VERIFIED"
    INVARIANT_VERIFIED = "INVARIANT_VERIFIED"
    DIFFERENTIALLY_VERIFIED = "DIFFERENTIALLY_VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"


@dataclasses.dataclass
class VerificationOutcome:
    is_valid: bool
    trust_level: str                  # from VerificationTrustLevel
    method: str
    absolute_error: float = 0.0
    relative_error: float = 0.0
    invariant_passed: bool = True
    confidence_score: float = 1.0     # 0.0 to 1.0
    details: Dict[str, Any] = dataclasses.field(default_factory=dict)
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "trust_level": self.trust_level,
            "method": self.method,
            "absolute_error": self.absolute_error,
            "relative_error": self.relative_error,
            "invariant_passed": self.invariant_passed,
            "confidence_score": self.confidence_score,
            "rejection_reason": self.rejection_reason,
            "details": self.details,
        }
