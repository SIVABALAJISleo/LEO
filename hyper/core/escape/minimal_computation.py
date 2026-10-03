"""
hyper/core/escape/minimal_computation.py
Minimal Sufficient Computation Engine (Prompt Section 6).
Finds the smallest computational obligation that satisfies the contract.
Optimizes jointly: arithmetic, memory traffic, synchronization, verification, and fallback cost.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from hyper.core.cost.ledger import EndToEndCostModel, WorkLedger
from hyper.core.contract.models import SemanticContract


class CandidateEscapePlan(BaseModel):
    plan_id: str
    engine_name: str
    estimated_work_reduction: float
    projected_cost_model: EndToEndCostModel
    ledger: WorkLedger
    is_exact: bool = True
    assumptions: List[str] = []


class MinimalSufficientComputation:
    """
    Selects the optimal execution pathway among candidate escape strategies,
    jointly minimizing FLOPs, memory bandwidth, verification, and fallback overhead.
    """

    @classmethod
    def select_cheapest_valid_plan(
        cls,
        candidates: List[CandidateEscapePlan],
        baseline_latency_ms: float,
        contract: SemanticContract,
    ) -> Optional[CandidateEscapePlan]:
        valid_plans = []
        for cand in candidates:
            # Check if expected end-to-end latency improves over baseline
            if cand.projected_cost_model.is_beneficial_over_baseline(baseline_latency_ms):
                valid_plans.append(cand)

        if not valid_plans:
            return None

        # Sort by total expected latency ascending
        valid_plans.sort(key=lambda p: p.projected_cost_model.compute_total_expected_latency_ms())
        return valid_plans[0]
