"""
tests/test_homotopic_contraction.py
===================================
Unit tests for Homotopic Path Contraction and Hoare Triple Invariant Pruning.
"""

import numpy as np
import pytest

from hyper.discovery.cir import CIRGraph, OpType, DataType
from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.exactness import ExactnessMode
from hyper.research_engine.homotopic_contraction import (
    HomotopicPathContractionEngine,
    HoareTriple,
)


def test_identity_add_contraction():
    # Build graph: Output = X + 0
    graph = CIRGraph(name="test_identity")
    in_x = graph.add_input("x", shape=(64, 64), dtype=DataType.FP32)
    zero_const = graph.add_constant("zero", value=0.0, dtype=DataType.FP32)
    add_node = graph.add_op(OpType.ADD, inputs=[in_x, zero_const], name="add_zero")
    graph.mark_output(add_node)

    contract = ProblemContract(
        workload_id="TEST_IDENTITY",
        description="Identity addition test",
        input_domain={"x": {"shape": [64, 64], "dtype": "FP32"}},
        output_domain={"out": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_mode=ExactnessMode.BIT_EXACT,
    )

    contracted_graph, report = HomotopicPathContractionEngine.contract_graph(graph, contract)

    assert report.original_node_count == 3
    assert report.contracted_node_count == 2  # add_node deleted
    assert add_node.node_id in report.deleted_nodes
    assert len(report.contracted_paths) >= 1
    assert "IDENTITY_ADD" in report.contracted_paths[0]
    # Output rewired directly to in_x
    assert contracted_graph.outputs == [in_x.node_id]


def test_annihilator_zero_contraction():
    # Build graph: Output = X * 0
    graph = CIRGraph(name="test_annihilator")
    in_x = graph.add_input("x", shape=(64, 64), dtype=DataType.FP32)
    zero_const = graph.add_constant("zero", value=0.0, dtype=DataType.FP32)
    mul_node = graph.add_op(OpType.MUL, inputs=[in_x, zero_const], name="mul_zero")
    graph.mark_output(mul_node)

    contract = ProblemContract(
        workload_id="TEST_ANNIHILATOR",
        description="Annihilator multiplication test",
        input_domain={"x": {"shape": [64, 64], "dtype": "FP32"}},
        output_domain={"out": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_mode=ExactnessMode.BIT_EXACT,
    )

    contracted_graph, report = HomotopicPathContractionEngine.contract_graph(graph, contract)
    assert any("ANNIHILATOR_ZERO" in p for p in report.contracted_paths)
    assert report.hoare_invariants_verified >= 3
