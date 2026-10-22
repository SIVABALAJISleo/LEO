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
        # Empirical crossover threshold from benchmarks/igpu_tiling_tuning.py: N >= 768
        if "INTEL_UHD_IGPU" in contract.permitted_backends and self.backend_registry.is_available("INTEL_UHD_IGPU"):
            has_beneficial_matmul = any(
                n.op_type == OpType.MATMUL and (n.shape and n.shape[0] >= 768 and n.shape[1] >= 768)
                for n in graph.nodes.values()
            )
            if has_beneficial_matmul:
                # Intel UHD iGPU delivers 1.3-1.5x speedup for N >= 768 with ~0.8ms dispatch overhead
                est_gpu_lat = max(0.5, (base_flops / (8e9)) * 1000.0)
                cost_gpu = self.cost_model.evaluate_cost(
                    estimated_latency_ms=est_gpu_lat,
                    memory_mb=base_mem * 1.1,
                    contract=contract,
                    is_exact=True,
                    is_accelerated=True,
                    dispatch_overhead_ms=0.8,
                )
                candidates.append(CandidatePlan(
                    plan_id="PLAN_INTEL_UHD_GPU",
                    target_backend="INTEL_UHD_IGPU",
                    graph=graph.clone(),
                    applied_rules=["OPENVINO_GPU_DISPATCH"],
                    is_exact=True,
                    estimated_flops=base_flops,
                    estimated_memory_mb=base_mem * 1.1,
                    cost_breakdown=cost_gpu,
                    rank_score=cost_gpu.total_cost_score,
                ))

        # Candidate 4: Automated Algorithmic Discovery via E-Graphs (Equality Saturation)
        try:
            from hyper_x.cpce.egraph import EqualitySaturationEngine
            egraph_engine = EqualitySaturationEngine()
            egraph, root_id = egraph_engine.build_egraph(graph)
            egraph_rules = egraph_engine.saturate(egraph)
            if egraph_rules:
                opt_egraph_g, _ = egraph_engine.extract_optimal_ast(egraph, root_id)
                egraph_flops = sum(n.resource_cost_flops for n in opt_egraph_g.nodes.values())
                egraph_mem = sum(n.memory_bytes for n in opt_egraph_g.nodes.values()) / (1024 * 1024)
                est_egraph_lat = max(0.01, (egraph_flops / 1e9) * 1000.0)

                cost_egraph = self.cost_model.evaluate_cost(
                    estimated_latency_ms=est_egraph_lat,
                    memory_mb=egraph_mem,
                    contract=contract,
                    is_exact=True,
                    is_accelerated=False,
                )
                candidates.append(CandidatePlan(
                    plan_id=f"PLAN_EGRAPH_SATURATION_{len(egraph_rules)}FUSIONS",
                    target_backend="CPU",
                    graph=opt_egraph_g,
                    applied_rules=egraph_rules,
                    is_exact=True,
                    estimated_flops=egraph_flops,
                    estimated_memory_mb=egraph_mem,
                    cost_breakdown=cost_egraph,
                    rank_score=cost_egraph.total_cost_score,
                ))
        except Exception:
            pass

        # Candidate 5: JIT Vectorized Kernel Emission (AVX2 parallel scaling / Horner)
        has_fusible_ops = any(n.op_type in (OpType.SCALE, OpType.HORNER_EVAL) for n in graph.nodes.values())
        if has_fusible_ops:
            jit_flops = sum(n.resource_cost_flops for n in graph.nodes.values())
            jit_mem = sum(n.memory_bytes for n in graph.nodes.values()) / (1024 * 1024)
            est_jit_lat = max(0.02, (jit_flops / 1.5e10) * 1000.0)
            cost_jit = self.cost_model.evaluate_cost(
                estimated_latency_ms=est_jit_lat,
                memory_mb=jit_mem,
                contract=contract,
                is_exact=True,
                is_accelerated=True,
            )
            candidates.append(CandidatePlan(
                plan_id="PLAN_JIT_NATIVE_KERNEL",
                target_backend="CPU",
                graph=graph.clone(),
                applied_rules=["JIT_KERNEL_EMISSION_AVX2"],
                is_exact=True,
                estimated_flops=jit_flops,
                estimated_memory_mb=jit_mem,
                cost_breakdown=cost_jit,
                rank_score=cost_jit.total_cost_score,
            ))

        # Candidate 6: Heterogeneous Subgraph Offloading (CPU + iGPU)
        if "INTEL_UHD_IGPU" in contract.permitted_backends and self.backend_registry.is_available("INTEL_UHD_IGPU"):
            has_dense = any(n.op_type == OpType.MATMUL and (n.shape and n.shape[0] >= 768) for n in graph.nodes.values())
            has_structural = any(n.op_type in (OpType.SCALE, OpType.HORNER_EVAL) for n in graph.nodes.values())
            if has_dense and has_structural:
                est_subgraph_lat = max(0.5, (base_flops / 9e9) * 1000.0)
                cost_subgraph = self.cost_model.evaluate_cost(
                    estimated_latency_ms=est_subgraph_lat,
                    memory_mb=base_mem * 1.15,
                    contract=contract,
                    is_exact=True,
                    is_accelerated=True,
                    dispatch_overhead_ms=0.5,
                )
                candidates.append(CandidatePlan(
                    plan_id="PLAN_HETEROGENEOUS_SUBGRAPH_OFFLOAD",
                    target_backend="INTEL_UHD_IGPU",
                    graph=graph.clone(),
                    applied_rules=["SUBGRAPH_PARTITION_OFFLOAD"],
                    is_exact=True,
                    estimated_flops=base_flops,
                    estimated_memory_mb=base_mem * 1.15,
                    cost_breakdown=cost_subgraph,
                    rank_score=cost_subgraph.total_cost_score,
                ))

        # Rank candidates by cost score (ascending)
        candidates.sort(key=lambda c: c.rank_score)
        return candidates[:budget.max_candidates]
