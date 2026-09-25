import numpy as np
import pytest

from hyper.discovery.cir import (
    CIRGraph,
    CIRTensorMeta,
    DataType,
    OpType,
)
from hyper.discovery.contract import (
    VerificationMode,
    WorkloadContract,
)
from hyper.discovery.search import (
    SearchConfig,
    SearchEngine,
    SearchStrategy,
)


def test_algebraic_reassociation_discovery_with_tolerance():
    """
    Test discovering A @ (B @ C) from (A @ B) @ C under NUMERIC_TOLERANCE.
    M=10, K=10, P=100, N=10.
    Cost left: 40,000 FLOPs.
    Cost right: 22,000 FLOPs.
    """
    g = CIRGraph(name="chained_gemm")
    in_a = g.add_input("A", shape=(10, 10), dtype=DataType.FP32)
    in_b = g.add_input("B", shape=(10, 100), dtype=DataType.FP32)
    in_c = g.add_input("C", shape=(100, 10), dtype=DataType.FP32)

    op_ab = g.add_op(OpType.MATMUL, [in_a, in_b], name="ab", output_meta=CIRTensorMeta(shape=(10, 100), dtype=DataType.FP32))
    op_abc = g.add_op(OpType.MATMUL, [op_ab, in_c], name="out", output_meta=CIRTensorMeta(shape=(10, 10), dtype=DataType.FP32))
    g.mark_output(op_abc)

    contract = WorkloadContract(
        contract_id="c_reassoc_tol_test",
        workload_name="chained_matmul",
        required_outputs=["out"],
        exactness_mode=VerificationMode.MODE_3_NUMERIC_TOLERANCE,
        tolerance_atol=1e-4,
        tolerance_rtol=1e-4,
    )

    np.random.seed(42)
    sample_inputs = {
        "A": np.random.randn(10, 10).astype(np.float32),
        "B": np.random.randn(10, 100).astype(np.float32),
        "C": np.random.randn(100, 10).astype(np.float32),
    }

    engine = SearchEngine()
    result = engine.discover(
        initial_graph=g,
        sample_inputs=sample_inputs,
        contract=contract,
        config=SearchConfig(strategy=SearchStrategy.A_STAR),
    )

    assert result.is_shortcut_found is True
    assert result.status_message == "SHORTCUT_DISCOVERED"
    assert result.best_cost < result.baseline_cost
    assert result.verification_record is not None
    assert result.verification_record.passed is True
    assert result.verification_record.parity_classification == "NUMERICAL_PARITY"


def test_algebraic_reassociation_strict_rejection():
    """
    FAILURE-FIRST DESIGN:
    When contract demands NUMERIC_EXACT (atol=0, ULP<=1), floating-point
    accumulation differences reject the reassociated candidate.
    """
    g = CIRGraph(name="chained_gemm_strict")
    in_a = g.add_input("A", shape=(10, 10), dtype=DataType.FP32)
    in_b = g.add_input("B", shape=(10, 100), dtype=DataType.FP32)
    in_c = g.add_input("C", shape=(100, 10), dtype=DataType.FP32)

    op_ab = g.add_op(OpType.MATMUL, [in_a, in_b], name="ab", output_meta=CIRTensorMeta(shape=(10, 100), dtype=DataType.FP32))
    op_abc = g.add_op(OpType.MATMUL, [op_ab, in_c], name="out", output_meta=CIRTensorMeta(shape=(10, 10), dtype=DataType.FP32))
    g.mark_output(op_abc)

    contract = WorkloadContract(
        contract_id="c_reassoc_strict_test",
        workload_name="chained_matmul_strict",
        required_outputs=["out"],
        exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
    )

    np.random.seed(42)
    sample_inputs = {
        "A": np.random.randn(10, 10).astype(np.float32),
        "B": np.random.randn(10, 100).astype(np.float32),
        "C": np.random.randn(100, 10).astype(np.float32),
    }

    engine = SearchEngine()
    result = engine.discover(
        initial_graph=g,
        sample_inputs=sample_inputs,
        contract=contract,
    )

    # Reassociated candidate was rejected due to floating point accumulation delta!
    # Engine falls back to baseline with NO_VERIFIED_SHORTCUT_FOUND
    assert result.is_shortcut_found is False
    assert result.status_message == "NO_VERIFIED_SHORTCUT_FOUND"
    assert any(t.action == "VERIFIED_FAIL" for t in result.search_trace)


def test_fallback_when_no_shortcut_found():
    """When a problem has no cheaper valid pathway, engine returns trusted baseline."""
    g = CIRGraph(name="simple_add")
    in_x = g.add_input("X", shape=(4, 4), dtype=DataType.FP32)
    in_y = g.add_input("Y", shape=(4, 4), dtype=DataType.FP32)
    out_node = g.add_op(OpType.ADD, [in_x, in_y], name="out", output_meta=CIRTensorMeta(shape=(4, 4), dtype=DataType.FP32))
    g.mark_output(out_node)

    contract = WorkloadContract(
        contract_id="c_add_test",
        workload_name="simple_addition",
        required_outputs=["out"],
        exactness_mode=VerificationMode.MODE_1_BIT_EXACT,
    )

    sample_inputs = {
        "X": np.ones((4, 4), dtype=np.float32),
        "Y": np.ones((4, 4), dtype=np.float32) * 2,
    }

    engine = SearchEngine()
    result = engine.discover(
        initial_graph=g,
        sample_inputs=sample_inputs,
        contract=contract,
    )

    assert result.is_shortcut_found is False
    assert result.status_message == "NO_VERIFIED_SHORTCUT_FOUND"
    assert result.best_pathway.graph.total_estimated_flops() == g.total_estimated_flops()
    assert result.verification_record.passed is True
