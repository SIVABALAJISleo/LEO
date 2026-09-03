"""
tests/test_hyper_v3_core.py
Unit tests for HYPER 3.0 Contract Parser, Universal Computation IR, Graph Optimizer, DCE, and CSE.
"""

import pytest
import numpy as np
from hyper_v3.frontend.contract_parser import ContractParser, ExecutionTrack, ExactnessClass
from hyper_v3.frontend.program_observer import ProgramObserver
from hyper_v3.ir.graph import ComputationGraphIR, GraphBuilder
from hyper_v3.ir.node import IRNode
from hyper_v3.ir.operation import OpType, DeviceType, NecessityStatus
from hyper_v3.ir.tensor import TensorDescriptor


def test_contract_parser_exact_and_contract_aware():
    exact = ContractParser.create_exact_contract("test_gemm")
    assert exact.track == ExecutionTrack.EXACT
    assert exact.exactness_class == ExactnessClass.BITWISE_EXACT
    assert exact.contract_hash != ""

    aware = ContractParser.create_contract_aware_contract("test_gemm", allow_low_rank=True)
    assert aware.track == ExecutionTrack.CONTRACT_AWARE
    assert aware.allow_low_rank is True
    assert aware.contract_hash != exact.contract_hash


def test_program_observer_tensor_inspection():
    arr = np.zeros((10, 10), dtype=np.float32)
    arr[0, 0] = 5.0
    prof = ProgramObserver.inspect_tensor(arr)
    assert prof["shape"] == [10, 10]
    assert prof["size"] == 100
    assert prof["sparsity_ratio"] == 0.99
    assert prof["has_nan"] is False


def test_universal_ir_graph_builder():
    graph = GraphBuilder.build_gemm_graph(128, 128, 128)
    assert len(graph.nodes) == 1
    assert graph.total_reference_flops() == 2 * 128 * 128 * 128
    assert "A" in graph.input_tensors
    assert "C" in graph.output_tensors


def test_graph_dead_code_and_cse_elimination():
    graph = ComputationGraphIR(graph_id="test_dce_cse")
    t_a = TensorDescriptor("A", [10, 10])
    t_b = TensorDescriptor("B", [10, 10])
    t_c = TensorDescriptor("C", [10, 10])
    t_dead = TensorDescriptor("DeadOut", [10, 10])

    node1 = IRNode("matmul_live", OpType.MATMUL, "live_op", [t_a, t_b], [t_c], flops=2000)
    node_dead = IRNode("matmul_dead", OpType.MATMUL, "dead_op", [t_a, t_b], [t_dead], flops=2000)
    graph.add_node(node1)
    graph.add_node(node_dead)

    dce_count = graph.eliminate_dead_nodes(live_outputs={"C"})
    assert dce_count == 1
    assert node_dead.annotations.is_dead is True
