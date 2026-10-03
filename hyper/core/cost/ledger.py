"""
hyper/core/cost/ledger.py
Work Ledger, Total Cost Model, and Verified Work Reduction (VWR) computation.
Never derives operation reduction from latency. Strict symbolic and instrumented FLOP accounting.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AccountingType(str, Enum):
    SYMBOLIC = "SYMBOLIC"
    INSTRUMENTED = "INSTRUMENTED"
    MEASURED = "MEASURED"
    ESTIMATED = "ESTIMATED"
    DERIVED = "DERIVED"
    SIMULATED = "SIMULATED"


class WorkLedger(BaseModel):
    """
    Authoritative Work Ledger tracking exact computational obligations and savings.
    """
    accounting_type: AccountingType = AccountingType.INSTRUMENTED
    baseline_symbolic_operations: int = 0
    candidate_symbolic_operations: int = 0
    baseline_executed_operations: int = 0
    candidate_executed_operations: int = 0
    operations_eliminated: int = 0
    memory_bytes_baseline: int = 0
    memory_bytes_candidate: int = 0
    verification_operations: int = 0
    fallback_operations: int = 0
    analysis_cost: int = 0
    preparation_cost: int = 0

    def calculate_work_reduction(self) -> float:
        """
        Verified Work Reduction (VWR):
        VWR = 1 - (candidate_verified_work / baseline_verified_work)
        """
        baseline = self.baseline_executed_operations or self.baseline_symbolic_operations
        candidate = (
            (self.candidate_executed_operations or self.candidate_symbolic_operations)
            + self.verification_operations
            + self.analysis_cost
            + self.preparation_cost
        )
        if baseline <= 0:
            return 0.0
        reduction = 1.0 - (candidate / float(baseline))
        return max(0.0, min(1.0, reduction))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accounting_type": self.accounting_type.value,
            "baseline_symbolic_operations": self.baseline_symbolic_operations,
            "candidate_symbolic_operations": self.candidate_symbolic_operations,
            "baseline_executed_operations": self.baseline_executed_operations,
            "candidate_executed_operations": self.candidate_executed_operations,
            "operations_eliminated": self.operations_eliminated,
            "memory_bytes_baseline": self.memory_bytes_baseline,
            "memory_bytes_candidate": self.memory_bytes_candidate,
            "verification_operations": self.verification_operations,
            "fallback_operations": self.fallback_operations,
            "analysis_cost": self.analysis_cost,
            "preparation_cost": self.preparation_cost,
            "verified_work_reduction_pct": round(self.calculate_work_reduction() * 100.0, 4),
        }


class EndToEndCostModel(BaseModel):
    """
    Joint Cost Function (Prompt Section 6 & 32):
    T_total = T_analysis + T_prep + T_candidate + T_verif + P(fail)*T_fallback + amortized(T_build) + T_output
    """
    t_analysis_ms: float = 0.0
    t_preparation_ms: float = 0.0
    t_candidate_ms: float = 0.0
    t_verification_ms: float = 0.0
    p_failure: float = 0.0
    t_fallback_ms: float = 0.0
    t_build_amortized_ms: float = 0.0
    t_output_ms: float = 0.0

    def compute_total_expected_latency_ms(self) -> float:
        return (
            self.t_analysis_ms
            + self.t_preparation_ms
            + self.t_candidate_ms
            + self.t_verification_ms
            + (self.p_failure * self.t_fallback_ms)
            + self.t_build_amortized_ms
            + self.t_output_ms
        )

    def is_beneficial_over_baseline(self, baseline_ms: float) -> bool:
        expected = self.compute_total_expected_latency_ms()
        return expected < baseline_ms
