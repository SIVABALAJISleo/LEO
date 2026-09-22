"""
hyper/discovery/meta_search.py
==============================
Meta-Search Strategy Ensemble & Dynamic Saturation Detector for UCTDE.

Higher-level search orchestrator:
  Selects best search strategy S* = argmax_S DiscoveryEfficiency(S, W)
  Strategies: EXHAUSTIVE, BEAM, GENETIC, MONTE_CARLO, BAYESIAN, SYNTHESIS, HYBRID.

Tracks saturation:
  d(BestCost) / d(Candidates) and d(BestCost) / d(Time).
  Labels: SEARCH_SATURATED (never fake 'UNIVERSAL_OPTIMUM_FOUND').
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchStrategyType(str, Enum):
    EXHAUSTIVE = "EXHAUSTIVE"
    BEAM = "BEAM"
    GENETIC = "GENETIC"
    MONTE_CARLO = "MONTE_CARLO"
    BAYESIAN = "BAYESIAN"
    PROGRAM_SYNTHESIS = "PROGRAM_SYNTHESIS"
    HYBRID = "HYBRID"


class StrategyEfficiencyMetric(BaseModel):
    strategy: SearchStrategyType
    workload_domain: str
    candidates_evaluated: int = 0
    breakthroughs_found: int = 0
    total_cost_reduction: float = 0.0
    total_time_ms: float = 0.0
    efficiency_score: float = 0.0             # cost reduction / time_ms

    def record_step(self, cost_reduction: float, time_ms: float, is_breakthrough: bool) -> None:
        self.candidates_evaluated += 1
        if is_breakthrough:
            self.breakthroughs_found += 1
        self.total_cost_reduction += max(0.0, cost_reduction)
        self.total_time_ms += max(0.001, time_ms)
        self.efficiency_score = (self.total_cost_reduction * 1000.0) / self.total_time_ms


class SearchSaturationReport(BaseModel):
    is_saturated: bool
    delta_cost_per_candidate: float
    delta_cost_per_time: float
    candidates_in_window: int
    epistemic_verdict: str                    # "SEARCH_SATURATED" or "CONTINUE_SEARCH"
    rationale: str


class MetaSearchEngine:
    """
    Selects, switches, and evaluates search strategies dynamically based on empirical yield.
    """

    def __init__(self) -> None:
        self.strategy_history: Dict[str, StrategyEfficiencyMetric] = {}
        self.cost_trajectory: List[float] = []
        self.time_trajectory: List[float] = []

    def _key(self, strategy: SearchStrategyType, domain: str) -> str:
        return f"{strategy.value}:{domain}"

    def select_strategy(self, workload_domain: str, budget_candidates: int) -> SearchStrategyType:
        """
        Picks strategy with highest historical efficiency for domain,
        or uses domain heuristic if insufficient prior history.
        """
        # Check historical efficiency
        domain_strats = [
            m for k, m in self.strategy_history.items()
            if m.workload_domain == workload_domain and m.candidates_evaluated >= 5
        ]

        if domain_strats:
            best = max(domain_strats, key=lambda m: m.efficiency_score)
            return best.strategy

        # Domain heuristic fallback
        if workload_domain in ("NUMERICAL_POLYNOMIAL", "ARITHMETIC"):
            return SearchStrategyType.PROGRAM_SYNTHESIS
        elif workload_domain in ("SORTING", "BOUNDED_SORTING"):
            return SearchStrategyType.BEAM
        elif workload_domain in ("MATRIX", "LINEAR_ALGEBRA"):
            return SearchStrategyType.HYBRID
        elif budget_candidates > 500:
            return SearchStrategyType.GENETIC
        else:
            return SearchStrategyType.BEAM

    def record_evaluation(
        self,
        strategy: SearchStrategyType,
        domain: str,
        best_cost: float,
        cost_reduction: float,
        step_time_ms: float,
        is_breakthrough: bool,
    ) -> None:
        key = self._key(strategy, domain)
        if key not in self.strategy_history:
            self.strategy_history[key] = StrategyEfficiencyMetric(
                strategy=strategy,
                workload_domain=domain,
            )
        self.strategy_history[key].record_step(cost_reduction, step_time_ms, is_breakthrough)
        self.cost_trajectory.append(best_cost)
        self.time_trajectory.append(time.time())

    def check_saturation(
        self,
        window_size: int = 15,
        cost_threshold: float = 1e-4,
    ) -> SearchSaturationReport:
        """
        Determines whether search has saturated (diminishing returns).
        Never reports UNIVERSAL_OPTIMUM_FOUND; reports SEARCH_SATURATED.
        """
        if len(self.cost_trajectory) < window_size:
            return SearchSaturationReport(
                is_saturated=False,
                delta_cost_per_candidate=1.0,
                delta_cost_per_time=1.0,
                candidates_in_window=len(self.cost_trajectory),
                epistemic_verdict="CONTINUE_SEARCH",
                rationale="Insufficient history window to establish saturation.",
            )

        recent_costs = self.cost_trajectory[-window_size:]
        recent_times = self.time_trajectory[-window_size:]

        cost_delta = abs(recent_costs[0] - recent_costs[-1])
        time_delta = max(0.001, recent_times[-1] - recent_times[0])

        d_cost_d_cand = cost_delta / float(window_size)
        d_cost_d_time = cost_delta / time_delta

        is_saturated = (d_cost_d_cand < cost_threshold)

        verdict = "SEARCH_SATURATED" if is_saturated else "CONTINUE_SEARCH"
        rationale = (
            f"Cost improvement over last {window_size} candidates is {d_cost_d_cand:.2e} "
            f"(threshold {cost_threshold:.2e}). "
            f"{'Diminishing returns reached; budget saturated.' if is_saturated else 'Progress actively continuing.'}"
        )

        return SearchSaturationReport(
            is_saturated=is_saturated,
            delta_cost_per_candidate=d_cost_d_cand,
            delta_cost_per_time=d_cost_d_time,
            candidates_in_window=window_size,
            epistemic_verdict=verdict,
            rationale=rationale,
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "strategies_tracked": len(self.strategy_history),
            "total_evaluations": len(self.cost_trajectory),
            "metrics": [m.model_dump() for m in self.strategy_history.values()],
        }


class FormalBarrierType(str, Enum):
    HARDWARE_BARRIER = "HARDWARE_BARRIER"
    MEMORY_BARRIER = "MEMORY_BARRIER"
    BANDWIDTH_BARRIER = "BANDWIDTH_BARRIER"
    COMPUTATIONAL_BARRIER = "COMPUTATIONAL_BARRIER"
    INFORMATION_BARRIER = "INFORMATION_BARRIER"
    CONTRACT_BARRIER = "CONTRACT_BARRIER"
    VERIFICATION_BARRIER = "VERIFICATION_BARRIER"
    SEARCH_BARRIER = "SEARCH_BARRIER"
    UNKNOWN = "UNKNOWN"


class BarrierClassification(BaseModel):
    barrier_type: FormalBarrierType
    confidence: float = 1.0
    rationale: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)


class FormalBarrierClassifier:
    """
    Identifies root cause computational barriers preventing further optimization.
    """

    @staticmethod
    def classify(
        entropy_score: float,
        memory_usage_mb: float,
        bandwidth_required_gbs: float,
        verification_failures: int,
        search_iterations: int,
    ) -> BarrierClassification:
        if bandwidth_required_gbs > 18.57:
            return BarrierClassification(
                barrier_type=FormalBarrierType.BANDWIDTH_BARRIER,
                confidence=0.95,
                rationale=f"Required bandwidth ({bandwidth_required_gbs:.2f} GB/s) exceeds STREAM-measured physical ceiling (18.57 GB/s).",
                evidence={"bandwidth_required": bandwidth_required_gbs, "measured_ceiling": 18.57},
            )
        elif memory_usage_mb > 14000.0:
            return BarrierClassification(
                barrier_type=FormalBarrierType.MEMORY_BARRIER,
                confidence=0.90,
                rationale="Workload footprint saturates 16 GB Unified System RAM.",
                evidence={"memory_usage_mb": memory_usage_mb},
            )
        elif entropy_score > 0.95:
            return BarrierClassification(
                barrier_type=FormalBarrierType.INFORMATION_BARRIER,
                confidence=0.88,
                rationale="High Shannon entropy denotes incompressible input data; no lossless representation escape possible.",
                evidence={"entropy": entropy_score},
            )
        elif verification_failures >= 5 and search_iterations >= 20:
            return BarrierClassification(
                barrier_type=FormalBarrierType.CONTRACT_BARRIER,
                confidence=0.85,
                rationale="Candidate pathways consistently violate strict contract error tolerances.",
                evidence={"failures": verification_failures, "iterations": search_iterations},
            )
        elif search_iterations > 100:
            return BarrierClassification(
                barrier_type=FormalBarrierType.SEARCH_BARRIER,
                confidence=0.80,
                rationale="Search space grammar exhausted without finding non-trivial pathway.",
                evidence={"iterations": search_iterations},
            )
        return BarrierClassification(
            barrier_type=FormalBarrierType.UNKNOWN,
            confidence=0.50,
            rationale="Insufficient evidence to attribute barrier to physical or theoretical limit.",
        )


class AdaptiveSearchScaler:
    """
    Scales candidate search budgets: 10 -> 100 -> 1,000 -> 10,000.
    Expands when discoveries and novelty are high; contracts/restarts when stagnated.
    """

    SCALING_TIERS = [10, 100, 1000, 10000, 100000]

    def __init__(self, initial_budget: int = 10) -> None:
        self.current_tier_idx = 0
        self.budget = self.SCALING_TIERS[self.current_tier_idx]

    def update_budget(self, discoveries_found: int, novelty_ratio: float, verification_yield: float) -> int:
        """
        Dynamically adjusts budget based on progress signals.
        """
        if discoveries_found > 0 and novelty_ratio > 0.60 and verification_yield > 0.50:
            # Scale up to next tier
            if self.current_tier_idx < len(self.SCALING_TIERS) - 1:
                self.current_tier_idx += 1
                self.budget = self.SCALING_TIERS[self.current_tier_idx]
        elif novelty_ratio < 0.20 or verification_yield < 0.10:
            # Stagnation: contract or restart tier
            if self.current_tier_idx > 0:
                self.current_tier_idx -= 1
                self.budget = self.SCALING_TIERS[self.current_tier_idx]

        return self.budget

