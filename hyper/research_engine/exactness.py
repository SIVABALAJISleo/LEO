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


class ExactnessCategory(str, enum.Enum):
    """
    Formal 4-tier computational exactness hierarchy mandated by HYPER Master Architecture.
    Never silently convert one category into another.
    """
    EXACT = "EXACT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    APPROXIMATE = "APPROXIMATE"
    HEURISTIC = "HEURISTIC"

    @property
    def is_exact(self) -> bool:
        return self == ExactnessCategory.EXACT

    @property
    def is_numerically_bounded(self) -> bool:
        return self in (
            ExactnessCategory.EXACT,
            ExactnessCategory.NUMERICALLY_EQUIVALENT,
            ExactnessCategory.APPROXIMATE,
        )

    def validate_claim(self, claimed_category: ExactnessCategory) -> bool:
        """
        Disallows upgrading a less rigorous category to a higher category.
        Precedence: EXACT (4) > NUMERICALLY_EQUIVALENT (3) > APPROXIMATE (2) > HEURISTIC (1).
        """
        ranks = {
            ExactnessCategory.EXACT: 4,
            ExactnessCategory.NUMERICALLY_EQUIVALENT: 3,
            ExactnessCategory.APPROXIMATE: 2,
            ExactnessCategory.HEURISTIC: 1,
        }
        return ranks[self] >= ranks[claimed_category]

    @classmethod
    def from_mode(cls, mode: ExactnessMode) -> ExactnessCategory:
        if mode in (ExactnessMode.BIT_EXACT, ExactnessMode.INTEGER_EXACT, ExactnessMode.SYMBOLIC_EXACT, ExactnessMode.NUMERIC_EXACT):
            return cls.EXACT
        elif mode in (ExactnessMode.NUMERIC_TOLERANCE, ExactnessMode.CONTRACT_EQUIVALENCE):
            return cls.NUMERICALLY_EQUIVALENT
        elif mode == ExactnessMode.PERCEPTUAL_EQUIVALENCE:
            return cls.APPROXIMATE
        return cls.HEURISTIC


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

    def to_category(self) -> ExactnessCategory:
        return ExactnessCategory.from_mode(self)

    def validate_claim(self, claimed_mode: ExactnessMode) -> bool:
        """
        Disallows upgrading a relaxed mode to an exact mode.
        A result computed under NUMERIC_TOLERANCE cannot claim BIT_EXACT.
        """
        if claimed_mode.is_truly_exact and not self.is_truly_exact:
            return False
        return True

