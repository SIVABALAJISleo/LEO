"""
hyper_x/cpce/__init__.py
========================
HYPER Computational Phase-Change Engine (CPCE) Package.
Integrates Representation Transformation, Sound Algebraic Rewriting,
Bounded Escape Search, CPU+iGPU Execution, and Independent Verification.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper_x.cpce.contracts import (
    WorkloadContract,
    ValidationMode,
    ExactnessRequirement,
    ContractRegistry,
)
from hyper_x.cpce.types import (
    TaggedMatrix,
    DenseMatrix,
    IdentityMatrix,
    ZeroMatrix,
    DiagonalMatrix,
    SparseMatrix,
    LowRankMatrix,
)
from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType
from hyper_x.cpce.structural_analysis import StructuralAnalyzer, StructuralMetadata
from hyper_x.cpce.rewrite_rules import (
    RewriteRule,
    ExactAlgebraicRewriter,
    IdentityEliminationRule,
    ZeroPropagationRule,
    DiagonalScalingRule,
    CommonSubexpressionEliminationRule,
    HornerPolynomialRule,
    DeadCodeEliminationRule,
)
from hyper_x.cpce.rewrite_verifier import (
    RewriteVerifier,
    VerificationOutcome,
    VerificationReport,
)
from hyper_x.cpce.cost_model import CPCECostModel, CostBreakdown
from hyper_x.cpce.algorithm_search import (
    CPCESearchEngine,
    SearchBudget,
    CandidatePlan,
)
from hyper_x.cpce.backend_registry import CPCEBackendRegistry, BackendDescriptor
from hyper_x.cpce.execution_planner import CPCEExecutionPlanner
from hyper_x.cpce.cache import CPCECache, CPCECacheKeyBuilder
from hyper_x.cpce.result_schema import (
    CPCEResult,
    ExecutionStatus,
    ProvenanceLabel,
)
from hyper_x.cpce.telemetry import CPCETelemetry, TelemetryRecord
from hyper_x.cpce.support_matrix import CPCESupportMatrix, SupportMatrixEntry


class ComputationalPhaseChangeEngine:
    """
    Master Orchestrator for the HYPER Computational Phase-Change Engine (CPCE).
    Transforms computational representations, discovers verified alternative execution plans,
    dispatches across CPU and Intel UHD iGPU, and certifies outputs independently.
    """

    def __init__(self):
        self.contracts = ContractRegistry()
        self.structural_analyzer = StructuralAnalyzer()
        self.rewriter = ExactAlgebraicRewriter()
        self.cost_model = CPCECostModel()
        self.backend_registry = CPCEBackendRegistry()
        self.search_engine = CPCESearchEngine(
            rewriter=self.rewriter,
            cost_model=self.cost_model,
            backend_registry=self.backend_registry,
        )
        self.execution_planner = CPCEExecutionPlanner(backend_registry=self.backend_registry)
        self.cache = CPCECache()
        self.support_matrix = CPCESupportMatrix()

    def build_canonical_graph_for_gemm(self, A: Any, B: Any) -> CanonicalGraph:
        """Constructs a CanonicalGraph for matrix multiplication C = A @ B."""
        g = CanonicalGraph(name="gemm_graph")
        node_a = CIRNode(node_id="A", op_type=OpType.INPUT, shape=getattr(A, "shape", None), dtype=str(getattr(A, "dtype", "float32")))
        node_b = CIRNode(node_id="B", op_type=OpType.INPUT, shape=getattr(B, "shape", None), dtype=str(getattr(B, "dtype", "float32")))

        self.structural_analyzer.tag_node(node_a, A)
        self.structural_analyzer.tag_node(node_b, B)

        # Flops for standard dense GEMM: 2 * M * N * K
        M = node_a.shape[0] if node_a.shape else 512
        K = node_a.shape[1] if node_a.shape else 512
        N = node_b.shape[1] if node_b.shape else 512
        nominal_flops = 2.0 * M * N * K

        node_c = CIRNode(
            node_id="C",
            op_type=OpType.MATMUL,
            inputs=["A", "B"],
            shape=(M, N),
            resource_cost_flops=nominal_flops,
            memory_bytes=M * N * 4,
        )
        node_out = CIRNode(node_id="output", op_type=OpType.OUTPUT, inputs=["C"], shape=(M, N))

        g.add_node(node_a)
        g.add_node(node_b)
        g.add_node(node_c)
        g.add_node(node_out)

        g.add_edge("A", "C")
        g.add_edge("B", "C")
        g.add_edge("C", "output")

        return g

    def execute_workload(
        self,
        contract_id: str,
        inputs: Dict[str, Any],
        reference_fn: Optional[Callable[[Dict[str, Any]], Any]] = None,
        use_cache: bool = True,
        search_budget: Optional[SearchBudget] = None,
    ) -> CPCEResult:
        """
        Executes end-to-end CPCE pipeline:
        1. Contract lookup and validation
        2. Cache query
        3. Canonical Graph construction
        4. Search for cheapest valid plan
        5. Execution & Verification
        6. Cache population & result sealing
        """
        contract = self.contracts.get(contract_id)
        if contract is None:
            raise KeyError(f"Contract '{contract_id}' not found in registry.")

        # 1. Cache lookup
        cache_key = None
        if use_cache:
            operands = list(inputs.values())
            cache_key = CPCECacheKeyBuilder.build_key(
                op_name=contract_id,
                operands=operands,
                contract=contract,
                backend="CPU",
            )
            cached_item = self.cache.get(cache_key)
            if cached_item is not None:
                cached_res, lookup_ms = cached_item
                res = CPCEResult(
                    status=ExecutionStatus.PASS,
                    contract_id=contract.contract_id,
                    contract_version=contract.version,
                    backend_requested="CACHE",
                    backend_used="CACHE_MEMORY",
                    device_identity="Host RAM Cache",
                    output=cached_res,
                    verification_status="PRE_VERIFIED_CACHE_HIT",
                    verification_evidence={"cache_hit": True, "cache_key": cache_key},
                    timings_ms={"lookup_ms": lookup_ms, "execution_ms": 0.0, "total_ms": lookup_ms},
                    resource_metrics={"cache_hit": True},
                    optimizations_applied=["VERIFIED_COMPUTATION_MEMOIZATION"],
                    provenance={"status": "MEASURED", "lookup": "MEASURED"},
                )
                res.seal()
                return res

        # 2. Graph Construction
        if "A" in inputs and "B" in inputs:
            graph = self.build_canonical_graph_for_gemm(inputs["A"], inputs["B"])
        elif "coefficients" in inputs and "x" in inputs:
            # Polynomial Horner Graph
            graph = CanonicalGraph(name="poly_horner_graph")
            deg = len(inputs["coefficients"])
            node_inp = CIRNode(node_id="poly_input", op_type=OpType.INPUT, parameters={"workload_type": "polynomial_expansion", "degree": deg})
            node_out = CIRNode(node_id="output", op_type=OpType.OUTPUT, inputs=["poly_input"])
            graph.add_node(node_inp)
            graph.add_node(node_out)
            graph.add_edge("poly_input", "output")
        else:
            # Generic Graph
            graph = CanonicalGraph(name=f"graph_{contract_id}")
            node_inp = CIRNode(node_id="in0", op_type=OpType.INPUT)
            node_out = CIRNode(node_id="output", op_type=OpType.OUTPUT, inputs=["in0"])
            graph.add_node(node_inp)
            graph.add_node(node_out)
            graph.add_edge("in0", "output")

        # 3. Search alternative execution plans
        candidates = self.search_engine.search_plans(graph, contract, budget=search_budget)
        best_plan = candidates[0]  # Lowest cost plan

        # 4. Dispatch and Execute
        result = self.execution_planner.execute_plan(
            plan=best_plan,
            inputs=inputs,
            contract=contract,
            reference_fn=reference_fn,
        )

        # 5. Populate cache if verified
        if use_cache and cache_key and result.status == ExecutionStatus.PASS:
            self.cache.put(cache_key, result.output, contract_id=contract.contract_id)

        return result

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic status of all CPCE engines and physical devices."""
        return {
            "engine": "HYPER Computational Phase-Change Engine (CPCE)",
            "status": "OPERATIONAL",
            "version": "1.0.0",
            "target_system": "Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5-13420H)",
            "backends": self.backend_registry.list_backends(),
            "contracts": self.contracts.list_contracts(),
            "cache_stats": self.cache.stats,
            "support_matrix_metrics": self.support_matrix.compute_summary_metrics(),
        }



__all__ = [
    "ComputationalPhaseChangeEngine",
    "WorkloadContract",
    "ValidationMode",
    "ExactnessRequirement",
    "ContractRegistry",
    "TaggedMatrix",
    "DenseMatrix",
    "IdentityMatrix",
    "ZeroMatrix",
    "DiagonalMatrix",
    "SparseMatrix",
    "LowRankMatrix",
    "CanonicalGraph",
    "CIRNode",
    "OpType",
    "StructuralAnalyzer",
    "StructuralMetadata",
    "RewriteRule",
    "ExactAlgebraicRewriter",
    "IdentityEliminationRule",
    "ZeroPropagationRule",
    "DiagonalScalingRule",
    "CommonSubexpressionEliminationRule",
    "HornerPolynomialRule",
    "DeadCodeEliminationRule",
    "RewriteVerifier",
    "VerificationOutcome",
    "VerificationReport",
    "CPCECostModel",
    "CostBreakdown",
    "CPCESearchEngine",
    "SearchBudget",
    "CandidatePlan",
    "CPCEBackendRegistry",
    "BackendDescriptor",
    "CPCEExecutionPlanner",
    "CPCECache",
    "CPCECacheKeyBuilder",
    "CPCEResult",
    "ExecutionStatus",
    "ProvenanceLabel",
    "CPCETelemetry",
    "TelemetryRecord",
    "CPCESupportMatrix",
    "SupportMatrixEntry",
]
