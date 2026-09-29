"""
tests/test_massive_search_and_discovery.py
==========================================
Validation suite for Phase 7 (Massive Pathway Search) & Phase 8 (Algorithm Discovery).
"""

import os
import tempfile
import numpy as np
import pytest

from hyper.research_engine.contracts import ComputationalContract
from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode
from hyper.research_engine.search_and_cost import (
    DominanceTable,
    MassivePathwaySearchEngine,
    PathwayGraph,
    PathwayGraphNode,
    SearchBudgetLevel,
    SearchOutcome,
)
from hyper.research_engine.algorithm_discovery import (
    AlgorithmDiscoveryEngine,
    AlgorithmDiscoveryRecord,
)


def test_pathway_graph_and_dominance_table():
    graph = PathwayGraph(workload_id="TEST_WORKLOAD")
    node1 = PathwayGraphNode(
        candidate_id="root",
        parent_id=None,
        transformation="CANONICAL",
        cost={"latency_ms": 10.0},
        verification_status="VERIFIED",
        resource_usage={"peak_ram": 1000},
        cir_hash="hash_root",
    )
    node2 = PathwayGraphNode(
        candidate_id="child1",
        parent_id="root",
        transformation="TILING",
        cost={"latency_ms": 6.0},
        verification_status="VERIFIED",
        resource_usage={"peak_ram": 800},
        cir_hash="hash_child1",
    )
    graph.add_node(node1)
    graph.add_node(node2)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.get_verified_nodes()) == 2

    # Dominance table test
    dt = DominanceTable()
    dt.update(latency_ms=10.0, memory_bytes=1000.0, error=0.0)
    # Better candidate (6.0 ms, 800 bytes) is NOT dominated
    assert dt.is_dominated(6.0, 800.0, 0.0) is False
    dt.update(latency_ms=6.0, memory_bytes=800.0, error=0.0)
    # Strictly worse candidate (12.0 ms, 1200 bytes, error=0.1) IS dominated
    assert dt.is_dominated(12.0, 1200.0, 0.1) is True


def test_massive_pathway_search_engine_execution():
    contract = ComputationalContract(
        workload_id="ML_MLP_INFERENCE",
        description="MLP Inference Test",
        input_domain={"x": {"shape": [1, 64], "dtype": "FP32"}},
        output_domain={"out": {"shape": [1, 10], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-3,
    )

    best_cand, best_cost, best_proof, outcome, graph = MassivePathwaySearchEngine.search(
        contract,
        budget_level=SearchBudgetLevel.LEVEL_1_FAST,
    )

    assert best_cand is not None
    assert best_proof.is_verified is True
    assert outcome in (SearchOutcome.FOUND, SearchOutcome.NOT_FOUND_WITHIN_BUDGET)
    assert len(graph.nodes) >= 1
    assert best_cost.execution_time_ms > 0


def test_algorithm_discovery_engine_produces_artifacts():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="GEMM Discovery Test",
        input_domain={
            "A": {"shape": [32, 32], "dtype": "FP32"},
            "B": {"shape": [32, 32], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-3,
    )

    record, best_cand, best_proof = AlgorithmDiscoveryEngine.discover_pathway(
        contract,
        budget=SearchBudgetLevel.LEVEL_2_EXPANDED,
    )

    assert best_proof.is_verified is True
    if record is not None:
        assert isinstance(record, AlgorithmDiscoveryRecord)
        assert record.workload_id == "GEMM_STANDARD"
        assert record.verification_status == "VERIFIED"
        assert os.path.exists(f"research/discoveries/{record.discovery_id}.json")
        assert os.path.exists(f"research/discoveries/{record.discovery_id}.md")
