import numpy as np
import pytest

from hyper.discovery.cir import (
    CIRGraph,
    CIRTensorMeta,
    DataType,
    OpType,
)


def test_cir_graph_basic_evaluation():
    g = CIRGraph(name="test_matmul_add")
    in_a = g.add_input("A", shape=(4, 8), dtype=DataType.FP32)
    in_b = g.add_input("B", shape=(8, 4), dtype=DataType.FP32)
    in_c = g.add_input("C", shape=(4, 4), dtype=DataType.FP32)

    op_mm = g.add_op(OpType.MATMUL, [in_a, in_b], name="mm")
    op_add = g.add_op(OpType.ADD, [op_mm, in_c], name="add_out")
    g.mark_output(op_add)

    # Topological order
    order = g.topological_sort()
    assert len(order) == 5

    # Evaluation
    np.random.seed(42)
    a_val = np.random.randn(4, 8).astype(np.float32)
    b_val = np.random.randn(8, 4).astype(np.float32)
    c_val = np.random.randn(4, 4).astype(np.float32)

    res = g.evaluate({"A": a_val, "B": b_val, "C": c_val})
    expected = (a_val @ b_val) + c_val
    np.testing.assert_allclose(res["add_out"], expected, rtol=1e-5, atol=1e-5)


def test_cir_serialization_roundtrip():
    g = CIRGraph(name="roundtrip_graph")
    in_x = g.add_input("X", shape=(2, 3), dtype=DataType.FP32)
    const_k = g.add_constant("K", np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32))
    op_mul = g.add_op(OpType.MUL, [in_x, const_k], name="out_mul")
    g.mark_output(op_mul)

    json_str = g.to_json()
    g_loaded = CIRGraph.from_json(json_str)

    assert g_loaded.name == "roundtrip_graph"
    assert len(g_loaded.nodes) == len(g.nodes)
    assert len(g_loaded.edges) == len(g.edges)

    x_val = np.ones((2, 3), dtype=np.float32)
    res_orig = g.evaluate({"X": x_val})
    res_loaded = g_loaded.evaluate({"X": x_val})
    np.testing.assert_array_equal(res_orig["out_mul"], res_loaded["out_mul"])


def test_cir_dead_node_elimination():
    g = CIRGraph(name="dead_node_graph")
    in_a = g.add_input("A", shape=(2, 2))
    in_b = g.add_input("B", shape=(2, 2))

    useful = g.add_op(OpType.ADD, [in_a, in_b], name="useful")
    dead = g.add_op(OpType.MUL, [in_a, in_b], name="dead")
    g.mark_output(useful)

    removed = g.eliminate_dead_nodes()
    assert removed == 1
    assert "dead" not in [n.name for n in g.nodes.values()]
    assert "useful" in [n.name for n in g.nodes.values()]
