"""
hyper_x/cpce/cost_model.py
==========================
Constrained Cost Model for CPCE.
Calculates realistic execution cost:
Cost = measured_end_to_end_latency_ms + memory_penalty + operational_risk_penalty.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional
from hyper_x.cpce.contracts import WorkloadContract


@dataclasses.dataclass
class CostBreakdown:
    setup_cost_ms: float = 0.0
    dispatch_cost_ms: float = 0.0
    kernel_execution_ms: float = 0.0
    verification_cost_ms: float = 0.0
    estimated_memory_mb: float = 0.0
    memory_penalty: float = 0.0
    risk_penalty: float = 0.0
    total_cost_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CPCECostModel:
    """
    Evaluates candidate execution plans using end-to-end latency and resource penalties.
    """

    def __init__(self, memory_penalty_weight: float = 0.05, risk_penalty_weight: float = 2.0):
        self.memory_penalty_weight = memory_penalty_weight
        self.risk_penalty_weight = risk_penalty_weight

    def evaluate_cost(
        self,
        estimated_latency_ms: float,
        memory_mb: float,
        contract: WorkloadContract,
        is_exact: bool = True,
        is_accelerated: bool = False,
        dispatch_overhead_ms: float = 0.05,
    ) -> CostBreakdown:
        """
        Computes total cost score for an execution plan.
        """
        # Memory penalty if exceeding contract budget
        mem_penalty = 0.0
        if memory_mb > contract.memory_budget_mb:
            excess = memory_mb - contract.memory_budget_mb
            mem_penalty = excess * 10.0  # Sharp penalty for exceeding RAM budget
        else:
            mem_penalty = memory_mb * self.memory_penalty_weight

        # Risk penalty if non-exact or requiring unverified conversion
        risk_penalty = 0.0 if is_exact else self.risk_penalty_weight

        # Dispatch overhead (higher for GPU dispatch on small matrices)
        setup_ms = dispatch_overhead_ms if is_accelerated else 0.01
        kernel_ms = max(0.001, estimated_latency_ms)
        verify_ms = 0.05 if is_exact else 0.15

        total_score = setup_ms + kernel_ms + verify_ms + mem_penalty + risk_penalty

        return CostBreakdown(
            setup_cost_ms=round(setup_ms, 3),
            dispatch_cost_ms=round(dispatch_overhead_ms, 3),
            kernel_execution_ms=round(kernel_ms, 3),
            verification_cost_ms=round(verify_ms, 3),
            estimated_memory_mb=round(memory_mb, 2),
            memory_penalty=round(mem_penalty, 3),
            risk_penalty=round(risk_penalty, 3),
            total_cost_score=round(total_score, 3),
        )
