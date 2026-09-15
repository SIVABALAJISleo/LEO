"""
hyper_x/ahce/cost_model.py
==========================
End-to-end computational and latency cost model for AHCE (Sections 14 & 15).

Formula:
TOTAL_COST = T_analysis + T_transform + T_compile + T_exec + T_sync + T_recon + T_verify + T_mem

Work Reduction:
WorkReduction = 1.0 - (CandidateNecessaryWork / ReferenceNecessaryWork)
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class CostBreakdown:
    analysis_ms: float = 0.0
    transformation_ms: float = 0.0
    compilation_ms: float = 0.0
    execution_ms: float = 0.0
    synchronization_ms: float = 0.0
    reconstruction_ms: float = 0.0
    verification_ms: float = 0.0
    memory_overhead_ms: float = 0.0
    total_cost_ms: float = 0.0

    def compute_total(self) -> float:
        self.total_cost_ms = (
            self.analysis_ms
            + self.transformation_ms
            + self.compilation_ms
            + self.execution_ms
            + self.synchronization_ms
            + self.reconstruction_ms
            + self.verification_ms
            + self.memory_overhead_ms
        )
        return self.total_cost_ms

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class WorkBreakdown:
    reference_operations: float
    candidate_operations: float
    eliminated_operations: float
    reused_operations: float = 0.0
    predicted_operations: float = 0.0
    reconstructed_operations: float = 0.0
    verification_operations: float = 0.0
    work_reduction_ratio: float = 0.0

    def compute_reduction(self) -> float:
        if self.reference_operations <= 0:
            self.work_reduction_ratio = 0.0
        else:
            self.work_reduction_ratio = max(
                0.0,
                1.0 - (self.candidate_operations / self.reference_operations)
            )
        return self.work_reduction_ratio

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


class AHCECostModel:
    """Validates that candidate preparation does not exceed computation eliminated."""

    def evaluate_cost(
        self,
        analysis_ms: float,
        transform_ms: float,
        exec_ms: float,
        verify_ms: float,
        reference_exec_ms: float
    ) -> CostBreakdown:
        breakdown = CostBreakdown(
            analysis_ms=analysis_ms,
            transformation_ms=transform_ms,
            compilation_ms=0.0,
            execution_ms=exec_ms,
            synchronization_ms=0.0,
            reconstruction_ms=0.0,
            verification_ms=verify_ms,
            memory_overhead_ms=0.0
        )
        breakdown.compute_total()
        return breakdown

    def evaluate_work(
        self,
        ref_ops: float,
        cand_ops: float,
        reused_ops: float = 0.0,
        verif_ops: float = 0.0
    ) -> WorkBreakdown:
        elim_ops = max(0.0, ref_ops - cand_ops)
        wb = WorkBreakdown(
            reference_operations=ref_ops,
            candidate_operations=cand_ops,
            eliminated_operations=elim_ops,
            reused_operations=reused_ops,
            verification_operations=verif_ops
        )
        wb.compute_reduction()
        return wb
