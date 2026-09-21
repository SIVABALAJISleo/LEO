"""
hyper/universal/search/adaptive_search.py
=========================================
Universal Adaptive Search Engine.
Scales search budgets dynamically: 10 -> 100 -> 1,000 -> 10,000...
Enforces the 10-level escalation ladder.
Tracks search saturation:
Reports: 'Search saturated within the tested search space and budget.'
Never reports: 'No better algorithm exists.'
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..pathways.schema import UniversalPathway
from ..pathways.generator import UniversalPathwayGenerator
from ..contracts.universal_contract import UniversalContract
from ..information.boundary_engine import InformationBoundaryProfile
from ..ranking.pareto_frontier import UniversalParetoFrontier, UniversalParetoPoint
from .escalation import EscalationLadder, EscalationLevel


@dataclasses.dataclass
class SearchBudget:
    max_candidates: int = 25
    max_time_seconds: float = 30.0
    escalation_start_level: int = 1
    max_escalation_level: int = 10


@dataclasses.dataclass
class AdaptiveSearchState:
    total_evaluated: int = 0
    total_verified: int = 0
    total_failed: int = 0
    best_latency_ms: float = float("inf")
    best_pathway: Optional[UniversalPathway] = None
    current_escalation_level: int = 1
    is_saturated: bool = False
    saturation_reason: Optional[str] = None
    outcome: str = "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_evaluated": self.total_evaluated,
            "total_verified": self.total_verified,
            "total_failed": self.total_failed,
            "best_latency_ms": self.best_latency_ms if self.best_latency_ms < float("inf") else None,
            "best_pathway": self.best_pathway.to_dict() if self.best_pathway else None,
            "current_escalation_level": self.current_escalation_level,
            "is_saturated": self.is_saturated,
            "saturation_reason": self.saturation_reason,
            "outcome": self.outcome,
        }


class UniversalAdaptiveSearch:
    """Orchestrates adaptive search with progressive escalation and budget bounds."""

    def __init__(self, generator: UniversalPathwayGenerator) -> None:
        self.generator = generator

    def search(
        self,
        workload: Any,
        contract: UniversalContract,
        profile: Optional[InformationBoundaryProfile],
        evaluate_fn: Callable[[UniversalPathway], Tuple[bool, str, float, float]],
        budget: SearchBudget,
    ) -> AdaptiveSearchState:
        state = AdaptiveSearchState(current_escalation_level=budget.escalation_start_level)
        t_start = time.perf_counter()
        consecutive_stagnant_evals = 0

        for level_idx in range(budget.escalation_start_level, budget.max_escalation_level + 1):
            state.current_escalation_level = level_idx

            if (time.perf_counter() - t_start) >= budget.max_time_seconds or state.total_evaluated >= budget.max_candidates:
                break

            # Generate candidate pool for current escalation level
            batch = self.generator.generate_candidate_pool(
                workload=workload,
                contract=contract,
                profile=profile,
                max_candidates=min(8, budget.max_candidates - state.total_evaluated),
            )

            if not batch:
                continue

            for pathway in batch:
                if (time.perf_counter() - t_start) >= budget.max_time_seconds or state.total_evaluated >= budget.max_candidates:
                    break

                state.total_evaluated += 1
                is_valid, trust, exec_ms, mem_mb = evaluate_fn(pathway)

                if is_valid:
                    state.total_verified += 1
                    if exec_ms < state.best_latency_ms:
                        state.best_latency_ms = exec_ms
                        state.best_pathway = pathway
                        state.outcome = "SUCCESS"
                        consecutive_stagnant_evals = 0
                    else:
                        consecutive_stagnant_evals += 1
                else:
                    state.total_failed += 1
                    consecutive_stagnant_evals += 1

                # Detect search saturation
                if consecutive_stagnant_evals >= 12:
                    state.is_saturated = True
                    state.saturation_reason = "Search saturated within the tested search space and budget."
                    break

            if state.is_saturated:
                break

        if state.outcome != "SUCCESS":
            state.outcome = "UNKNOWN"

        return state
