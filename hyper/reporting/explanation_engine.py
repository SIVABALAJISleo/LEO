"""
hyper/reporting/explanation_engine.py
=====================================
HYPER Optimization Explanation Engine:
Provides human-readable and structured scientific explanations for every
optimization decision made by the system.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class OptimizationExplanation:
    optimization_id: str
    problem: str
    baseline_work: str
    hyper_decision: str
    reason: str
    work_eliminated_pct: float
    work_reused_pct: float
    algorithm_used: str
    expected_benefit: str
    measured_benefit: str
    correctness_status: str
    quality_impact: str
    fallback_condition: str


class OptimizationExplanationEngine:
    """Maintains a ledger of transparent optimization rationales."""
    def __init__(self):
        self.explanations: List[OptimizationExplanation] = []

    def record_decision(
        self,
        optimization_id: str,
        problem: str,
        baseline_work: str,
        hyper_decision: str,
        reason: str,
        work_eliminated_pct: float,
        work_reused_pct: float,
        algorithm_used: str,
        expected_benefit: str,
        measured_benefit: str,
        correctness_status: str = "PASS",
        quality_impact: str = "PASS (SSIM >= 0.96)",
        fallback_condition: str = "Confidence < 0.35 -> Full Compute",
    ) -> OptimizationExplanation:
        entry = OptimizationExplanation(
            optimization_id=optimization_id,
            problem=problem,
            baseline_work=baseline_work,
            hyper_decision=hyper_decision,
            reason=reason,
            work_eliminated_pct=work_eliminated_pct,
            work_reused_pct=work_reused_pct,
            algorithm_used=algorithm_used,
            expected_benefit=expected_benefit,
            measured_benefit=measured_benefit,
            correctness_status=correctness_status,
            quality_impact=quality_impact,
            fallback_condition=fallback_condition,
        )
        self.explanations.append(entry)
        return entry

    def export_summary(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self.explanations]
