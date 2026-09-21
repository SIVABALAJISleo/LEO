"""
hyper/universal/verification/schema.py
======================================
Formal Verification States and Scientific Outcomes.
7 Verification States & 4 Scientific Outcomes.
Rule: Zero Self-Confirmation. Candidate never verifies itself.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional


class VerificationState(str, Enum):
    EXACT_VERIFIED = "EXACT_VERIFIED"
    NUMERICALLY_VERIFIED = "NUMERICALLY_VERIFIED"
    INVARIANT_VERIFIED = "INVARIANT_VERIFIED"
    DIFFERENTIALLY_VERIFIED = "DIFFERENTIALLY_VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"


class ScientificOutcome(str, Enum):
    SUCCESS = "SUCCESS"                     # Verified candidate satisfies the contract
    FAILURE = "FAILURE"                     # Candidate violated contract
    UNKNOWN = "UNKNOWN"                     # No conclusion has been established
    BARRIER = "BARRIER"                     # Fundamental limitation proven or empirical barrier classified


@dataclasses.dataclass
class UniversalVerificationResult:
    is_valid: bool
    state: VerificationState
    scientific_outcome: ScientificOutcome
    method_used: str
    absolute_error: float = 0.0
    relative_error: float = 0.0
    confidence_score: float = 1.0
    rejection_reason: Optional[str] = None
    details: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "state": self.state.value,
            "scientific_outcome": self.scientific_outcome.value,
            "method_used": self.method_used,
            "absolute_error": self.absolute_error,
            "relative_error": self.relative_error,
            "confidence_score": self.confidence_score,
            "rejection_reason": self.rejection_reason,
            "details": self.details,
        }
