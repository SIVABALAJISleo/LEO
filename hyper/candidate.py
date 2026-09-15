"""
hyper/candidate.py
==================
Execution Candidate Result Model for LEO/HYPER.
Fulfills Phase 4 of the Master Architectural Specification.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Set


class PathClass(str, Enum):
    """Allowed candidate execution path classes."""
    EXACT = "EXACT"
    CACHED = "CACHED"
    REDUCED_WORK = "REDUCED_WORK"
    NUMERICALLY_APPROXIMATE = "NUMERICALLY_APPROXIMATE"
    PERCEPTUAL = "PERCEPTUAL"
    PREDICTIVE = "PREDICTIVE"
    FALLBACK_EXACT = "FALLBACK_EXACT"


ALLOWED_PATH_CLASSES: Set[str] = {p.value for p in PathClass}


@dataclass
class CandidateResult:
    """
    Standard result model for any computation candidate executed within the runtime.
    """
    value: Any
    path_class: str
    backend: str
    latency_ms: float
    work_units: Optional[int]
    memory_bytes: Optional[int]
    max_abs_error: Optional[float]
    relative_error: Optional[float]
    rmse: Optional[float]
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    cache_hit: bool = False
    prediction_used: bool = False
    fallback_used: bool = False
    verification_status: str = "UNVERIFIED"
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.path_class not in ALLOWED_PATH_CLASSES:
            raise ValueError(
                f"Invalid path_class '{self.path_class}'. Must be one of {sorted(ALLOWED_PATH_CLASSES)}"
            )
        if self.latency_ms < 0:
            raise ValueError(f"latency_ms cannot be negative, got {self.latency_ms}")
