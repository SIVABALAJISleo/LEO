"""
hyper/firewall/exactness_firewall.py
===================================
Exactness Firewall (Section 43):
System-wide type/classification barrier that prevents accidental mixing of:
EXACT, APPROXIMATE, PREDICTIVE, CACHED, REDUCED_WORK, SIMULATED, UNVERIFIED.
Guarantees a cached approximation is never silently presented as exact computation.
"""

from enum import Enum
from typing import Any, Dict


class ExactnessType(str, Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    PREDICTIVE = "PREDICTIVE"
    CACHED = "CACHED"
    REDUCED_WORK = "REDUCED_WORK"
    SIMULATED = "SIMULATED"
    UNVERIFIED = "UNVERIFIED"


class ExactnessViolationError(Exception):
    """Raised when an approximate or unverified result attempts to fulfill an EXACT contract."""
    pass


class ExactnessFirewall:
    """
    Guards output boundaries against contract/type mismatch.
    """
    def __init__(self):
        pass

    def validate_output_type(self, result_type: ExactnessType, required_type: ExactnessType) -> bool:
        if required_type == ExactnessType.EXACT and result_type != ExactnessType.EXACT:
            raise ExactnessViolationError(
                f"Exactness Firewall Block: Cannot serve result of type '{result_type.value}' "
                f"to satisfy strict contract requirement '{required_type.value}'."
            )
        return True
