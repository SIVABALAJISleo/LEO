"""
tests/v8/test_v8_nwc.py
=======================
Tests for NecessaryWorkGraph, NecessaryWorkMap, DependencyAnalyzer, and NWCMetrics.
"""

import numpy as np
import pytest

from hyper.v8.nwc import (
    NecessaryWorkGraph,
    NecessaryWorkMap,
    NecessityLabel,
    ChangeLabel,
    OpNode,
    DependencyAnalyzer,
    ChangeDetectionEngine,
)


def test_nwc_graph_construction():
    graph = NecessaryWorkGraph()
    node_a = OpNode(node_id="input_A", op_name="input", input_ids=[])
    node_b = OpNode(node_id="input_B", op_name="input", input_ids=[])
    node_c = OpNode(node_id="gemm_op", op_name="matmul", input_ids=["input_A", "input_B"])

    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)
    graph.mark_output("gemm_op")

    assert "gemm_op" in graph.nodes
    assert len(graph.nodes["gemm_op"].input_ids) == 2


def test_change_detection_engine():
    engine = ChangeDetectionEngine()
    arr1 = np.ones((10, 10), dtype=np.float32)
    arr2 = arr1.copy()
    arr3 = arr1.copy()
    arr3[0, 0] = 99.0

    assert engine.classify(arr1, "node_1") == ChangeLabel.UNKNOWN   # First registration
    assert engine.classify(arr2, "node_1") == ChangeLabel.UNCHANGED # Identical contents
    assert engine.classify(arr3, "node_1") == ChangeLabel.DEPENDENT # Modified contents


def test_dependency_analyzer_matmul():
    # When rows 0 and 2 of A change in 10x10 @ 10x10
    analysis = DependencyAnalyzer.analyze_matmul(
        a_changed_rows={0, 2},
        b_changed_cols=None,
        m=10,
        k=10,
        n=10,
    )
    assert analysis["affected_rows"] == [0, 2]
    assert analysis["fraction_affected"] == 0.2
    assert analysis["analysis"] == "PARTIAL_RECOMPUTE"
