"""
tests/test_hyper_v3_intelligence.py
Unit tests for the 9-dimensional computation intelligence engine.
"""

import pytest
import numpy as np
from hyper_v3.frontend.contract_parser import ContractParser
from hyper_v3.intelligence.necessity import NecessityAnalyzer
from hyper_v3.intelligence.redundancy import RedundancyAnalyzer
from hyper_v3.intelligence.structure import StructureAnalyzer
from hyper_v3.intelligence.sparsity import SparsityAnalyzer
from hyper_v3.intelligence.reuse import ReuseAnalyzer
from hyper_v3.intelligence.information import InformationAnalyzer
from hyper_v3.intelligence.complexity import ComplexityAnalyzer
from hyper_v3.intelligence.dependency import DependencyAnalyzer
from hyper_v3.intelligence.bottleneck import BottleneckAnalyzer
from hyper_v3.ir.graph import GraphBuilder


def test_necessity_analyzer():
    contract = ContractParser.create_contract_aware_contract("dense_gemm_fp32", allow_low_rank=True)
    report = NecessityAnalyzer.analyze("dense_gemm_fp32", contract)
    assert report.work_avoidance_potential > 0.0
    assert "output_consumption" in report.dimension_scores
    assert len(report.dimension_scores) >= 15


def test_redundancy_and_structure():
    mat_sym = np.array([[2.0, 1.0], [1.0, 3.0]])
    struct = StructureAnalyzer.analyze_matrix(mat_sym)
    assert struct["is_symmetric"] is True
    assert struct["is_square"] is True

    frame1 = np.ones((64, 64))
    frame2 = np.ones((64, 64))
    coherence = RedundancyAnalyzer.measure_temporal_coherence(frame1, frame2)
    assert coherence == 1.0


def test_sparsity_and_information():
    sparse_mat = np.zeros((10, 10))
    sparse_mat[0, 0] = 1.0
    s_un = SparsityAnalyzer.measure_unstructured_sparsity(sparse_mat)
    assert s_un == 0.99

    entropy = InformationAnalyzer.compute_shannon_entropy(np.random.randn(100))
    assert entropy > 0.0


def test_complexity_dependency_bottleneck():
    comp = ComplexityAnalyzer.estimate_gemm_complexity(100, 100, 100, "strassen")
    assert comp["complexity_class"] == "O(N^2.807)"

    graph = GraphBuilder.build_gemm_graph(64, 64, 64)
    crit = DependencyAnalyzer.find_critical_path(graph)
    assert crit["total_nodes"] == 1

    node = list(graph.nodes.values())[0]
    bottle = BottleneckAnalyzer.classify_node(node)
    assert bottle["bottleneck"] in ["COMPUTE_BOUND", "MEMORY_BOUND", "BALANCED"]
