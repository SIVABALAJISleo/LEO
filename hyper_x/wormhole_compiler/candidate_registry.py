"""
hyper_x/wormhole_compiler/candidate_registry.py
=============================================================================
HYPER-X Candidate & Failure Knowledge Registry: Versioned Reproducibility
=============================================================================
Stores and versions discovered algorithm candidates with full cryptographic
provenance hashes.

Also implements "Failure as Knowledge" (Phase 44):
Persists failed and falsified candidates with their failure mode, input traits,
and diagnosis to prevent the evolution engine from repeating known bad transformations.
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

from hyper_x.wormhole_compiler.schemas import (
    CandidateAlgorithmRecord,
    FailureCategory,
)


@dataclass
class FailureRecord:
    failure_id: str
    grammar_expression: str
    target_operation: str
    failure_category: FailureCategory
    measured_error: float
    tolerance: float
    input_characteristics: Dict[str, Any]
    diagnosis: str
    timestamp: float = field(default_factory=time.time)


class CandidateRegistry:
    """Versioned candidate catalog and failure knowledge base."""

    def __init__(self):
        self.verified_candidates: Dict[str, CandidateAlgorithmRecord] = {}
        self.failure_knowledge_base: List[FailureRecord] = []

    def register_verified_candidate(self, candidate: CandidateAlgorithmRecord) -> None:
        """Registers a candidate that has passed verification, falsification, and holdout."""
        self.verified_candidates[candidate.candidate_id] = candidate

    def record_failure(
        self,
        grammar_expression: str,
        target_operation: str,
        failure_category: FailureCategory,
        measured_error: float,
        tolerance: float,
        input_characteristics: Dict[str, Any],
        diagnosis: str
    ) -> FailureRecord:
        """Persists failure record to guide future search away from dead ends."""
        f_id = f"FAIL_{int(time.time()*1000)%100000}"
        rec = FailureRecord(
            failure_id=f_id,
            grammar_expression=grammar_expression,
            target_operation=target_operation,
            failure_category=failure_category,
            measured_error=measured_error,
            tolerance=tolerance,
            input_characteristics=input_characteristics,
            diagnosis=diagnosis
        )
        self.failure_knowledge_base.append(rec)
        return rec

    def is_known_failure(
        self,
        grammar_expression: str,
        input_traits: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Checks if a grammar expression previously failed under similar input traits."""
        for fail in self.failure_knowledge_base:
            if fail.grammar_expression == grammar_expression:
                # Check rank or sparsity similarity
                fail_rank = fail.input_characteristics.get("rank_ratio", 1.0)
                curr_rank = input_traits.get("rank_ratio", 1.0)
                if abs(fail_rank - curr_rank) < 0.15:
                    return True, f"Known failure ({fail.failure_category.value}): {fail.diagnosis}"
        return False, None

    def list_candidates(self) -> List[Dict[str, Any]]:
        return [asdict(c) for c in self.verified_candidates.values()]

    def to_json(self, indent: int = 2) -> str:
        return json.dumps({
            "verified_candidates": [asdict(c) for c in self.verified_candidates.values()],
            "failures_recorded": [asdict(f) for f in self.failure_knowledge_base]
        }, indent=indent)
