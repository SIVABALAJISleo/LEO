"""
tests/test_hyper_v2_core.py
Unit and property tests for HYPER 2.0 Compiler, IR, and Analyzers.
"""

import pytest
import numpy as np
from hyper_v2.compiler.contract_compiler import ContractCompiler, ExecutionContract, ExecutionTrack
from hyper_v2.compiler.intermediate_representation import ComputationGraphIR, IRNode, TensorSpec, OpCategory
from hyper_v2.compiler.graph_builder import GraphBuilder
from hyper_v2.compiler.graph_optimizer import GraphOptimizer
from hyper_v2.analysis.necessity_analyzer import NecessityAnalyzer
from hyper_v2.analysis.redundancy_analyzer import RedundancyAnalyzer
from hyper_v2.analysis.structure_analyzer import StructureAnalyzer
from hyper_v2.analysis.sparsity_analyzer import SparsityAnalyzer


def test_contract_compiler_immutable():
    spec = {
        "workload_id": "gemm_test",
        "track": "TRACK_B_CONTRACT",
        "numerical_tolerance": 1e-3,
        "latency_target_ms": 16.6
    }
    contract = ContractCompiler.compile_contract(spec)
    assert contract.workload_id == "gemm_test"
    assert contract.track == ExecutionTrack.TRACK_B_CONTRACT
    assert contract.numerical_tolerance == 1e-3
    assert len(contract.compute_hash()) == 16


def test_graph_builder_and_optimizer():
    graph = GraphBuilder.build_gemm_graph(M=512, N=512, K=512, sparsity=0.6)
    assert graph.total_flops == 2 * 512 * 512 * 512
    assert "matmul_0" in graph.nodes

    contract = ExecutionContract(workload_id="gemm_test", allowed_transformations={"sparsity", "kernel_fusion"})
    opt_graph = GraphOptimizer.optimize_graph(graph, contract)
    assert opt_graph.total_flops < graph.total_flops


def test_necessity_analyzer():
    graph = GraphBuilder.build_gemm_graph(M=256, N=256, K=256)
    contract = ExecutionContract(workload_id="gemm_test", allowed_transformations={"low_rank"})
    report = NecessityAnalyzer.analyze_workload(graph, contract, sample_inputs={"sparsity_ratio": 0.5})
    assert report.original_flops > 0
    assert report.work_avoided_ratio > 0.0
    assert report.confidence_score > 0.8
    assert len(report.elimination_reasons) > 0


def test_redundancy_and_sparsity_analyzers():
    # Sparsity check
    arr = np.zeros((100, 100))
    arr[0, 0] = 1.0
    res = SparsityAnalyzer.analyze_sparsity(arr)
    assert res["is_sparse"] is True
    assert res["sparsity_ratio"] > 0.99

    # Structure check
    sym_matrix = np.array([[2.0, 1.0], [1.0, 3.0]])
    struct = StructureAnalyzer.analyze_matrix_structure(sym_matrix)
    assert struct["is_symmetric"] is True
