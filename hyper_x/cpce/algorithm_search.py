"""
hyper_x/cpce/algorithm_search.py
================================
Bounded Computational Escape Search Engine for CPCE.
Discovers valid alternative execution plans under time and candidate budgets.
Optimizes the constrained cost objective:
Cost = measured/estimated latency + memory penalty + risk penalty.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType
from hyper_x.cpce.contracts import WorkloadContract
from hyper_x.cpce.rewrite_rules import ExactAlgebraicRewriter
from hyper_x.cpce.cost_model import CPCECostModel, CostBreakdown
from hyper_x.cpce.backend_registry import CPCEBackendRegistry


@dataclasses.dataclass
class SearchBudget:
    max_candidates: int = 10
    max_search_time_ms: float = 500.0


@dataclasses.dataclass
class CandidatePlan:
    plan_id: str
    target_backend: str
    graph: CanonicalGraph
    applied_rules: List[str]
    is_exact: bool
    estimated_flops: float
    estimated_memory_mb: float
    cost_breakdown: CostBreakdown
    rank_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "target_backend": self.target_backend,
            "applied_rules": self.applied_rules,
            "is_exact": self.is_exact,
            "estimated_flops": float(self.estimated_flops),
            "estimated_memory_mb": float(self.estimated_memory_mb),
            "cost_breakdown": self.cost_breakdown.to_dict(),
            "rank_score": float(self.rank_score),
        }


class CPCESearchEngine:
    """
    Search engine that generates, prunes, and ranks alternative execution plans.
    """

    def __init__(
        self,
        rewriter: Optional[ExactAlgebraicRewriter] = None,
        cost_model: Optional[CPCECostModel] = None,
        backend_registry: Optional[CPCEBackendRegistry] = None,
    ):
        self.rewriter = rewriter or ExactAlgebraicRewriter()
        self.cost_model = cost_model or CPCECostModel()
        self.backend_registry = backend_registry or CPCEBackendRegistry()

    def search_plans(
        self,
        graph: CanonicalGraph,
        contract: WorkloadContract,
        budget: Optional[SearchBudget] = None,
    ) -> List[CandidatePlan]:
        """
        Explores candidate transformation pathways within the search budget.
        Returns candidates ranked from lowest cost to highest.
        """
        budget = budget or SearchBudget()
        t_start = time.perf_counter()
        candidates: List[CandidatePlan] = []

        # Candidate 1: Baseline Direct Execution on CPU
        base_flops = sum(n.resource_cost_flops for n in graph.nodes.values())
        base_mem = sum(n.memory_bytes for n in graph.nodes.values()) / (1024 * 1024)
        est_base_lat = max(0.1, (base_flops / 1e9) * 1000.0)

        cost_base = self.cost_model.evaluate_cost(
            estimated_latency_ms=est_base_lat,
            memory_mb=base_mem,
            contract=contract,
            is_exact=True,
            is_accelerated=False,
        )
        candidates.append(CandidatePlan(
            plan_id="PLAN_BASELINE_CPU",
            target_backend="CPU",
            graph=graph.clone(),
            applied_rules=[],
            is_exact=True,
            estimated_flops=base_flops,
            estimated_memory_mb=base_mem,
            cost_breakdown=cost_base,
            rank_score=cost_base.total_cost_score,
        ))

        # Check search budget time
        if (time.perf_counter() - t_start) * 1000.0 >= budget.max_search_time_ms:
            return candidates

        # Candidate 2: Rewritten Graph via Exact Algebraic Shortcuts
        rewritten_g, rules = self.rewriter.rewrite(graph)
        if rules:
            opt_flops = sum(n.resource_cost_flops for n in rewritten_g.nodes.values())
            opt_mem = sum(n.memory_bytes for n in rewritten_g.nodes.values()) / (1024 * 1024)
            est_opt_lat = max(0.01, (opt_flops / 1e9) * 1000.0)

            cost_opt = self.cost_model.evaluate_cost(
                estimated_latency_ms=est_opt_lat,
                memory_mb=opt_mem,
                contract=contract,
                is_exact=True,
                is_accelerated=False,
            )
            candidates.append(CandidatePlan(
                plan_id=f"PLAN_ALGEBRAIC_ESCAPE_{len(rules)}RULES",
                target_backend="CPU",
                graph=rewritten_g,
                applied_rules=rules,
                is_exact=True,
                estimated_flops=opt_flops,
                estimated_memory_mb=opt_mem,
                cost_breakdown=cost_opt,
                rank_score=cost_opt.total_cost_score,
            ))

        # Candidate 3: Intel UHD iGPU Acceleration (if available & permitted)
        if "INTEL_UHD_IGPU" in contract.permitted_backends and self.backend_registry.is_available("INTEL_UHD_IGPU"):
            # Check if graph has significant matrix operations (e.g. M, N >= 128)
            has_heavy_matmul = any(
                n.op_type == OpType.MATMUL and (n.shape and n.shape[0] >= 128)
                for n in graph.nodes.values()
            )
            if has_heavy_matmul:
                # Accelerator has dispatch overhead (~0.5ms) but higher parallel throughput
                est_gpu_lat = max(0.2, (base_flops / (5e9)) * 1000.0)
                cost_gpu = self.cost_model.evaluate_cost(
                    estimated_latency_ms=est_gpu_lat,
                    memory_mb=base_mem * 1.2,
                    contract=contract,
                    is_exact=True,
                    is_accelerated=True,
                    dispatch_overhead_ms=0.5,
                )
                candidates.append(CandidatePlan(
                    plan_id="PLAN_INTEL_UHD_GPU",
                    target_backend="INTEL_UHD_IGPU",
                    graph=graph.clone(),
                    applied_rules=["OPENVINO_GPU_DISPATCH"],
                    is_exact=True,
                    estimated_flops=base_flops,
                    estimated_memory_mb=base_mem * 1.2,
                    cost_breakdown=cost_gpu,
                    rank_score=cost_gpu.total_cost_score,
                ))

        # Rank candidates by cost score (ascending)
        candidates.sort(key=lambda c: c.rank_score)
        return candidates[:budget.max_candidates]
