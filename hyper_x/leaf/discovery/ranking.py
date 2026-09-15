"""
hyper_x/leaf/discovery/ranking.py
=================================
Multi-objective ranking engine for computational escape candidates.

Rule (Phase 25):
    Candidate score must include:
    - correctness
    - contract compliance
    - work reduction
    - memory reduction
    - end-to-end latency
    - verification overhead
    - generalization
    - reproducibility
    Do not collapse all of these into one magic number.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .candidate import EscapeCandidate


@dataclass(frozen=True)
class CandidateMultiScore:
    """Disjoint multi-dimensional evaluation score."""
    candidate_id: str
    is_correct: bool
    contract_compliance_ratio: float  # 0.0 to 1.0
    work_reduction_ratio: float       # 0.0 to 1.0 (1.0 = 100% eliminated)
    memory_reduction_ratio: float     # 0.0 to 1.0
    end_to_end_speedup: float         # ref_time / cand_time
    verification_overhead_ms: float
    generalization_score: float       # 0.0 to 1.0
    reproducibility_verified: bool
    breakthrough_level: str


class CandidateRanker:
    """Ranks candidates using Pareto domination rather than a single collapsed scalar."""

    def evaluate_candidate(
        self,
        candidate: EscapeCandidate,
        is_correct: bool,
        measured_ref_ms: float,
        measured_cand_ms: float,
        verification_ms: float,
        ref_mem_bytes: int,
        cand_mem_bytes: int,
        generalization_score: float = 1.0,
        reproducibility: bool = True,
    ) -> CandidateMultiScore:
        total_cand_ms = measured_cand_ms + verification_ms
        speedup = float(measured_ref_ms) / max(1e-6, total_cand_ms)
        mem_red = 1.0 - (float(cand_mem_bytes) / max(1, ref_mem_bytes))

        return CandidateMultiScore(
            candidate_id=candidate.candidate_id,
            is_correct=is_correct,
            contract_compliance_ratio=1.0 if is_correct else 0.0,
            work_reduction_ratio=candidate.work_reduction_ratio,
            memory_reduction_ratio=max(0.0, mem_red),
            end_to_end_speedup=speedup,
            verification_overhead_ms=verification_ms,
            generalization_score=generalization_score,
            reproducibility_verified=reproducibility,
            breakthrough_level=candidate.breakthrough_level.value,
        )

    def rank_candidates(self, scores: List[CandidateMultiScore]) -> List[CandidateMultiScore]:
        """Sorts primarily by correctness and contract compliance, then by end-to-end speedup."""
        return sorted(
            scores,
            key=lambda s: (
                1 if s.is_correct and s.reproducibility_verified else 0,
                s.contract_compliance_ratio,
                s.end_to_end_speedup,
                s.work_reduction_ratio,
            ),
            reverse=True,
        )
