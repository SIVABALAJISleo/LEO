"""
hyper/escape_engine/search/search_state.py
==========================================
VAEE Section 11 & 16: Adaptive Search State & Convergence Tracker.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional

from ..pathways.schema import ComputationalPathway


@dataclasses.dataclass
class CandidateEvaluation:
    pathway: ComputationalPathway
    is_verified: bool
    verification_level: str
    latency_ms: float
    memory_mb: float
    speedup_vs_baseline: float
    timestamp: float = dataclasses.field(default_factory=time.time)
    error_note: Optional[str] = None


@dataclasses.dataclass
class SearchState:
    experiment_id: str
    contract_id: str
    baseline_latency_ms: float = 0.0
    best_latency_ms: float = float("inf")
    best_pathway: Optional[ComputationalPathway] = None
    
    total_evaluated: int = 0
    total_verified: int = 0
    total_failed: int = 0
    
    saturation_detected: bool = False
    saturation_reason: Optional[str] = None
    outcome: str = "UNKNOWN"           # "SUCCESS" | "FAILURE" | "UNKNOWN" | "BARRIER"
    
    evaluations: List[CandidateEvaluation] = dataclasses.field(default_factory=list)
    recent_improvements: List[float] = dataclasses.field(default_factory=list)

    def record_evaluation(
        self,
        pathway: ComputationalPathway,
        is_verified: bool,
        verification_level: str,
        latency_ms: float,
        memory_mb: float,
    ) -> CandidateEvaluation:
        self.total_evaluated += 1
        speedup = (self.baseline_latency_ms / max(1e-6, latency_ms)) if self.baseline_latency_ms > 0 else 1.0

        if is_verified:
            self.total_verified += 1
            if latency_ms < self.best_latency_ms:
                improvement = (self.best_latency_ms - latency_ms) if self.best_latency_ms != float("inf") else 0.0
                self.recent_improvements.append(improvement)
                self.best_latency_ms = latency_ms
                self.best_pathway = pathway
                self.outcome = "SUCCESS"
        else:
            self.total_failed += 1

        ev = CandidateEvaluation(
            pathway=pathway,
            is_verified=is_verified,
            verification_level=verification_level,
            latency_ms=latency_ms,
            memory_mb=memory_mb,
            speedup_vs_baseline=round(speedup, 3),
        )
        self.evaluations.append(ev)
        return ev

    @property
    def improvement_rate(self) -> float:
        """Delta BestCost / Delta Candidates over last 10 evaluations."""
        if len(self.recent_improvements) < 2 or self.total_evaluated == 0:
            return 0.0
        return sum(self.recent_improvements[-10:]) / min(10, len(self.recent_improvements))
