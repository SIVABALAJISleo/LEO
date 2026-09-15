"""
hyper_x/leaf/discovery/candidate.py
===================================
Computational Escape Candidate definition and breakthrough classification.

Breakthrough Levels (Phase 26):
    LEVEL 0: Ordinary optimization
    LEVEL 1: Representation optimization
    LEVEL 2: Known algorithmic improvement
    LEVEL 3: Novel composition
    LEVEL 4: Exact reduced-computation pathway
    LEVEL 5: Genuinely new computational escape
    INVALID: Benchmark artifact, workload substitution, hidden cache,
             approximation mislabeled exact, self-verification, or simulated result.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from ..contract import LeafContract


class BreakthroughLevel(str, Enum):
    LEVEL_0 = "LEVEL_0_ORDINARY_OPTIMIZATION"
    LEVEL_1 = "LEVEL_1_REPRESENTATION_OPTIMIZATION"
    LEVEL_2 = "LEVEL_2_KNOWN_ALGORITHMIC_IMPROVEMENT"
    LEVEL_3 = "LEVEL_3_NOVEL_COMPOSITION"
    LEVEL_4 = "LEVEL_4_EXACT_REDUCED_COMPUTATION"
    LEVEL_5 = "LEVEL_5_NEW_COMPUTATIONAL_ESCAPE"
    INVALID = "INVALID"


@dataclass
class EscapeCandidate:
    """Represents a discovered computational escape pathway."""
    candidate_id: str
    workload_name: str
    pathway_type: str                          # "SYMBOLIC", "IMPLICIT", "NEURAL", "RESIDUAL", "HYBRID"
    reference_algorithm: str
    candidate_algorithm: str
    contract: LeafContract
    assumptions: List[str]
    representation: str
    reference_work_flops: int
    candidate_work_flops: int
    breakthrough_level: BreakthroughLevel
    failure_conditions: List[str]
    is_verified: bool = False
    measured_speedup: float = 1.0
    computational_compression_ratio: float = 1.0

    @property
    def work_reduction_ratio(self) -> float:
        if self.reference_work_flops <= 0:
            return 0.0
        return 1.0 - (float(self.candidate_work_flops) / self.reference_work_flops)
