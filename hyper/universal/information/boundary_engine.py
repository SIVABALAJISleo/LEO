"""
hyper/universal/information/boundary_engine.py
==============================================
Information Boundary Engine.
Distinguishes NECESSARY WORK, POTENTIALLY REDUNDANT WORK, and UNKNOWN WORK.
Evaluates:
- Information compressibility & entropy
- Sparsity & structure
- Dead input dimension elimination
- Output-directed requirements (only compute what is needed)
- Intermediate value avoidance (fusion opportunity)
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional

from ..adapter.workload_adapter import UniversalWorkload
from ..adapter.workload_types import WorkloadNecessityClass
from ..contracts.universal_contract import UniversalContract
from .entropy_analyzer import EntropyAnalyzer
from .dependency_pruner import DependencyPruner


@dataclasses.dataclass
class InformationBoundaryProfile:
    workload_id: str
    entropy_analysis: Dict[str, Any]
    dependency_analysis: Dict[str, Any]
    sparsity_ratio: float
    is_compressible: bool
    necessity_breakdown: Dict[str, float]  # percentages for REQUIRED, REDUNDANT, UNKNOWN
    reduction_opportunities: List[str]
    has_output_directed_potential: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "entropy_analysis": self.entropy_analysis,
            "dependency_analysis": self.dependency_analysis,
            "sparsity_ratio": self.sparsity_ratio,
            "is_compressible": self.is_compressible,
            "necessity_breakdown": self.necessity_breakdown,
            "reduction_opportunities": self.reduction_opportunities,
            "has_output_directed_potential": self.has_output_directed_potential,
        }


class InformationBoundaryEngine:
    """Probes the mathematical information bounds of arbitrary workloads."""

    @staticmethod
    def analyze(workload: UniversalWorkload, contract: UniversalContract) -> InformationBoundaryProfile:
        entropy = EntropyAnalyzer.analyze_entropy(workload.sample_input)
        dep = DependencyPruner.probe_input_dependencies(workload.target_fn, workload.sample_input)

        sparsity = entropy.get("sparsity_ratio", 0.0)
        is_comp = entropy.get("is_compressible", False)

        opportunities: List[str] = []
        if sparsity > 0.3:
            opportunities.append("SPARSITY_SKIPPING")
        if is_comp:
            opportunities.append("LOW_RANK_OR_COMPRESSION")
        if dep.get("has_dead_dimensions", False):
            opportunities.append("DEAD_DIMENSION_PRUNING")
        if contract.latency_requirement_ms and contract.latency_requirement_ms < 10.0:
            opportunities.append("PRECOMPUTED_LOOKUP_OR_EARLY_EXIT")

        # Estimate necessity distribution
        redundant_est = min(0.6, sparsity * 0.5 + (0.2 if is_comp else 0.0))
        required_est = max(0.2, 1.0 - redundant_est - 0.1)
        unknown_est = max(0.0, 1.0 - required_est - redundant_est)

        breakdown = {
            WorkloadNecessityClass.REQUIRED.value: round(required_est * 100.0, 1),
            WorkloadNecessityClass.REDUNDANT.value: round(redundant_est * 100.0, 1),
            WorkloadNecessityClass.UNKNOWN.value: round(unknown_est * 100.0, 1),
        }

        has_output_dir = False
        if workload.schema.output_shape and workload.schema.input_shape:
            # If output is substantially smaller than input (e.g. reduction, top-k, classification)
            in_elems = workload.schema.element_count
            out_elems = 1
            if workload.schema.output_shape:
                import math
                out_elems = math.prod(workload.schema.output_shape)
            if out_elems < in_elems * 0.5:
                has_output_dir = True
                opportunities.append("OUTPUT_DIRECTED_PRUNING")

        return InformationBoundaryProfile(
            workload_id=workload.workload_id,
            entropy_analysis=entropy,
            dependency_analysis=dep,
            sparsity_ratio=sparsity,
            is_compressible=is_comp,
            necessity_breakdown=breakdown,
            reduction_opportunities=opportunities,
            has_output_directed_potential=has_output_dir,
        )
