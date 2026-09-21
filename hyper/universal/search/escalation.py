"""
hyper/universal/search/escalation.py
====================================
Section 37: 10-Level Escalation Ladder.
When initial optimizations fail to reach target parity, dynamically expand the search space:
Level 1: Local compiler optimizations
Level 2: Algorithmic transformations
Level 3: Representation transformations
Level 4: Structural reductions
Level 5: Incremental computation
Level 6: Program synthesis
Level 7: Alternative mathematical formulations
Level 8: Radically different algorithm families
Level 9: Hybrid composed pathways
Level 10: Continuous adaptive search
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Dict, List, Optional
from ..pathways.schema import TransformationFamily


class EscalationLevel(IntEnum):
    LEVEL_1_LOCAL = 1
    LEVEL_2_ALGORITHMIC = 2
    LEVEL_3_REPRESENTATION = 3
    LEVEL_4_STRUCTURAL = 4
    LEVEL_5_INCREMENTAL = 5
    LEVEL_6_PROGRAM_SYNTHESIS = 6
    LEVEL_7_MATHEMATICAL = 7
    LEVEL_8_RADICAL_FAMILIES = 8
    LEVEL_9_HYBRID_COMPOSED = 9
    LEVEL_10_CONTINUOUS_ADAPTIVE = 10


class EscalationLadder:
    """Controls progressive expansion of the transformation search space."""

    LEVEL_TO_FAMILIES = {
        EscalationLevel.LEVEL_1_LOCAL: [TransformationFamily.COMPILER],
        EscalationLevel.LEVEL_2_ALGORITHMIC: [TransformationFamily.ALGORITHMIC],
        EscalationLevel.LEVEL_3_REPRESENTATION: [TransformationFamily.REPRESENTATION],
        EscalationLevel.LEVEL_4_STRUCTURAL: [TransformationFamily.STRUCTURAL],
        EscalationLevel.LEVEL_5_INCREMENTAL: [TransformationFamily.INCREMENTAL],
        EscalationLevel.LEVEL_6_PROGRAM_SYNTHESIS: [TransformationFamily.PROGRAM_SYNTHESIS],
        EscalationLevel.LEVEL_7_MATHEMATICAL: [TransformationFamily.MATHEMATICAL],
        EscalationLevel.LEVEL_8_RADICAL_FAMILIES: [TransformationFamily.OUTPUT_DIRECTED, TransformationFamily.SCHEDULING],
        EscalationLevel.LEVEL_9_HYBRID_COMPOSED: [TransformationFamily.MATHEMATICAL, TransformationFamily.ALGORITHMIC, TransformationFamily.STRUCTURAL],
        EscalationLevel.LEVEL_10_CONTINUOUS_ADAPTIVE: list(TransformationFamily),
    }

    @staticmethod
    def get_families_for_level(level: EscalationLevel) -> List[TransformationFamily]:
        return EscalationLadder.LEVEL_TO_FAMILIES.get(level, list(TransformationFamily))
