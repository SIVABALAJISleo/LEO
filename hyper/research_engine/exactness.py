"""
hyper/research_engine/exactness.py
==================================
Formal Computational Exactness Modes.

Every computational result and verified transformation in HYPER must explicitly
declare its exactness mode. Strict scientific discipline:
- NUMERIC_TOLERANCE must never be reported as BIT_EXACT.
- PERCEPTUAL_EQUIVALENCE must never be reported as EXACT COMPUTATION.
"""

from __future__ import annotations
import enum
from typing import Any, Dict


class ExactnessMode(str, enum.Enum):
    BIT_EXACT = "BIT_EXACT"
    INTEGER_EXACT = "INTEGER_EXACT"
    SYMBOLIC_EXACT = "SYMBOLIC_EXACT"
    NUMERIC_EXACT = "NUMERIC_EXACT"
    NUMERIC_TOLERANCE = "NUMERIC_TOLERANCE"
    CONTRACT_EQUIVALENCE = "CONTRACT_EQUIVALENCE"
    PERCEPTUAL_EQUIVALENCE = "PERCEPTUAL_EQUIVALENCE"

    @property
    def is_truly_exact(self) -> bool:
        """Returns True if the mode represents mathematical or bit-level exactness without loss."""
        return self in (
            ExactnessMode.BIT_EXACT,
            ExactnessMode.INTEGER_EXACT,
            ExactnessMode.SYMBOLIC_EXACT,
            ExactnessMode.NUMERIC_EXACT,
        )

    @property
    def allows_numerical_slack(self) -> bool:
        """Returns True if the mode admits finite-precision floating-point tolerance."""
        return self in (
            ExactnessMode.NUMERIC_TOLERANCE,
            ExactnessMode.CONTRACT_EQUIVALENCE,
            ExactnessMode.PERCEPTUAL_EQUIVALENCE,
        )

    def validate_claim(self, claimed_mode: ExactnessMode) -> bool:
        """
        Disallows upgrading a relaxed mode to an exact mode.
        A result computed under NUMERIC_TOLERANCE cannot claim BIT_EXACT.
        """
        if claimed_mode.is_truly_exact and not self.is_truly_exact:
            return False
        return True
