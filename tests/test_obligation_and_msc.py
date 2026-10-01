"""
tests/test_obligation_and_msc.py
================================
Test suite for:
- Computational Obligation Analyzer (COA)
- Minimal Sufficient Computation (MSC) & Computational Obligation Reduction (COR)
- Output-Directed Computation (Top-K selection & Trace projection)
- "Change the Problem" Reformulation Engine (FFT convolution, Sparse GEMM, Temporal Delta, Prediction+Residual)
- HYPER-SLA Engine & The Four 100% Master Metrics
"""

import numpy as np
import pytest

from hyper.contracts.contract import Contract
from hyper.contracts.sla_engine import ApplicationSLA, HyperSLAEngine, FourMasterMetrics
from hyper.universal_ir.opcodes import CIROpcode
from hyper.universal_ir.program import CIRProgram, CIRInstruction
from hyper.obligation.coa import (
    ComputationalObligationAnalyzer,
    ObligationClassification,
    DependencyType,
)
from hyper.obligation.msc import (
    MinimalSufficientComputationEngine,
    ComputationalObligationScore,
)
from hyper.escape.reformulation import (
    ReformulationEngine,
    ReformulationType,
)


def test_coa_backward_slicing_and_dead_code_elimination():
    """
    Verify that COA performs backward slicing from declared outputs,
    identifying dead unobserved branches and marking them as DEAD.
    """
    program = CIRProgram(name="dead_branch_test")
    # Instruction 0: live path (x + y -> a)
    program.add_instruction(CIRInstruction(op=CIROpcode.ADD, inputs=["x", "y"], output="a"))
    # Instruction 1: dead branch (x * z -> dead_1)
    program.add_instruction(CIRInstruction(op=CIROpcode.MUL, inputs=["x", "z"], output="dead_1"))
    # Instruction 2: dead branch continued (dead_1 + dead_1 -> dead_2)
    program.add_instruction(CIRInstruction(op=CIROpcode.ADD, inputs=["dead_1", "dead_1"], output="dead_2"))
    # Instruction 3: live path continued (a * 2 -> out)
    program.add_instruction(CIRInstruction(op=CIROpcode.MUL, inputs=["a", "two"], output="out"))
    program.outputs = ["out"]

    coa = ComputationalObligationAnalyzer()
    graph = coa.analyze(program=program, target_outputs=["out"])

    assert len(graph.nodes) == 4
    # Check that live nodes are REQUIRED
    live_node_0 = graph.nodes["node_0_ADD"]
    live_node_3 = graph.nodes["node_3_MUL"]
    assert live_node_0.classification == ObligationClassification.REQUIRED
    assert live_node_3.classification == ObligationClassification.REQUIRED

    # Check that dead nodes are classified as DEAD
    dead_node_1 = graph.nodes["node_1_MUL"]
    dead_node_2 = graph.nodes["node_2_ADD"]
    assert dead_node_1.classification == ObligationClassification.DEAD
    assert dead_node_1.is_dead is True
    assert dead_node_2.classification == ObligationClassification.DEAD
    assert dead_node_2.is_dead is True

    summary = graph.summary()
    assert summary["classification_breakdown"]["DEAD"] == 2
    assert summary["classification_breakdown"]["REQUIRED"] == 2
    assert summary["eliminated_flops"] > 0


def test_msc_sliced_execution_matches_golden():
    """
    Verify that MSC executes only the sliced required computation and
    produces identical results to golden reference while recording eliminated work.
    """
    program = CIRProgram(name="compute_pipeline")
    program.add_instruction(CIRInstruction(op=CIROpcode.ADD, inputs=["x", "y"], output="a"))
    program.add_instruction(CIRInstruction(op=CIROpcode.RELU, inputs=["a"], output="b"))
    program.add_instruction(CIRInstruction(op=CIROpcode.MUL, inputs=["x", "x"], output="unused_sq"))
    program.outputs = ["b"]

    x = np.array([-2.0, 1.0, 3.0], dtype=np.float32)
    y = np.array([3.0, -4.0, 2.0], dtype=np.float32)
    inputs = {"x": x, "y": y}

    msc = MinimalSufficientComputationEngine()
    result = msc.optimize_and_execute(program=program, inputs=inputs, target_outputs=["b"])

    # Golden reference: relu(x + y) = relu([1.0, -3.0, 5.0]) = [1.0, 0.0, 5.0]
    expected = np.maximum(x + y, 0)
    np.testing.assert_allclose(result.outputs["b"], expected, rtol=1e-6)

    # Verify work elimination
    assert result.score.eliminated_flops > 0
    assert result.score.computational_obligation_reduction > 0.0
    assert "unused_sq" not in result.outputs


def test_msc_output_directed_topk_selection():
    """
    Verify output-directed Top-K: MSC performs O(N) selection instead of O(N log N)
    full sort, achieving identical values and order with provable work elimination.
    """
    np.random.seed(42)
    n = 10000
    k = 10
    arr = np.random.randn(n).astype(np.float32)

    # Reference full sort
    sorted_full_indices = np.argsort(-arr)[:k]
    expected_topk_vals = arr[sorted_full_indices]

    msc = MinimalSufficientComputationEngine()
    dummy_prog = CIRProgram(name="topk_prog")
    res = msc.optimize_and_execute(
        program=dummy_prog,
        inputs={"arr": arr},
        query_type="TOPK",
        query_params={"k": k, "array_name": "arr"},
    )

    np.testing.assert_allclose(res.outputs["values"], expected_topk_vals, rtol=1e-6)
    assert res.score.original_work_flops > res.score.provably_required_flops
    assert res.score.computational_obligation_reduction > 0.5  # Significant COR


def test_msc_scalar_projection_trace():
    """
    Verify output-directed Trace(A @ B): MSC computes sum_ij (A_ij * B_ji)
    in O(M*K) without materializing the M x M intermediate matrix.
    """
    np.random.seed(42)
    m = 200
    k = 100
    A = np.random.randn(m, k).astype(np.float32)
    B = np.random.randn(k, m).astype(np.float32)

    # Reference baseline: explicit A @ B then np.trace
    expected_trace = float(np.trace(A @ B))

    msc = MinimalSufficientComputationEngine()
    dummy_prog = CIRProgram(name="trace_prog")
    res = msc.optimize_and_execute(
        program=dummy_prog,
        inputs={"A": A, "B": B},
        query_type="TRACE_MATMUL",
    )

    actual_trace = float(res.outputs["trace"])
    np.testing.assert_allclose(actual_trace, expected_trace, rtol=1e-4)
    # Original: 2*200*100*200 = 8,000,000 FLOPs. MSC: 2*200*100 = 40,000 FLOPs.
    assert res.score.computational_obligation_reduction > 0.95


def test_reformulation_fft_convolution():
    """
    Verify Reformulation Engine: Time-domain convolution -> Frequency-domain FFT
    produces mathematically equivalent output within IEEE-754 tolerance with O(N log N) complexity.
    """
    np.random.seed(42)
    signal = np.random.randn(4096).astype(np.float32)
    kernel = np.random.randn(256).astype(np.float32)

    engine = ReformulationEngine()
    res = engine.reformulate_convolution_to_frequency(signal, kernel)

    assert res.verification_passed is True
    assert res.max_abs_error < 1e-4
    assert res.baseline_flops == 2 * 4096 * 256
    assert res.work_reduction_ratio > 0.5


def test_reformulation_sparse_gemm():
    """
    Verify Reformulation Engine: Sparse GEMM skips zero entries and
    matches dense reference exactly.
    """
    np.random.seed(42)
    A = np.random.randn(64, 64).astype(np.float32)
    # Induce 80% sparsity
    A[np.abs(A) < 1.3] = 0.0
    B = np.random.randn(64, 32).astype(np.float32)

    engine = ReformulationEngine()
    res = engine.reformulate_sparse_gemm(A, B)

    assert res.verification_passed is True
    assert res.max_abs_error < 1e-4
    assert res.reformulated_flops < res.baseline_flops
    assert res.work_reduction_ratio > 0.5


def test_reformulation_temporal_delta():
    """
    Verify Reformulation Engine: Temporal delta processing updates only
    changed rows and reconstructs exact output.
    """
    np.random.seed(42)
    m, k, n = 50, 40, 20
    prev_x = np.random.randn(m, k).astype(np.float32)
    weights = np.random.randn(k, n).astype(np.float32)
    prev_y = prev_x @ weights

    # Current input with only 2 rows changed
    curr_x = prev_x.copy()
    curr_x[5, :] += 1.5
    curr_x[12, :] -= 0.8

    engine = ReformulationEngine()
    res = engine.reformulate_temporal_delta(curr_x, prev_x, prev_y, weights)

    assert res.verification_passed is True
    assert res.max_abs_error < 1e-5
    # Work reduction should be ~ (50 - 2) / 50 = 96%
    assert res.work_reduction_ratio > 0.90


def test_reformulation_prediction_plus_residual():
    """
    Verify Reformulation Engine: Prediction + Residual Correction guarantees
    exact numerical reconstruction within IEEE-754 precision.
    """
    signal = np.linspace(0, 10, 100, dtype=np.float32)
    # Expensive operator: sin(x) + cos(2x)
    exact_op = lambda s: np.sin(s) + np.cos(2 * s)
    # Cheap predictor: linear trend
    predictor = lambda s: 0.1 * s

    engine = ReformulationEngine()
    res = engine.reformulate_prediction_plus_residual(signal, predictor, exact_op)

    assert res.verification_passed is True
    assert res.max_abs_error < 1e-6


def test_hyper_sla_closure_success():
    """
    Verify HYPER-SLA Engine: Workload meeting all SLA requirements (latency,
    accuracy, determinism) achieves 100% Contract Performance Closure.
    """
    sla = ApplicationSLA(
        workload_name="fast_matrix_pipeline",
        required_latency_ms=100.0,
        required_accuracy=1.0,
        require_determinism=True,
    )

    A = np.ones((50, 50), dtype=np.float32)
    ref = A @ A
    execute_fn = lambda: A @ A

    engine = HyperSLAEngine()
    measurement = engine.evaluate_workload(sla, execute_fn, ref, repetitions=3)

    assert measurement.contract_closure is True
    assert measurement.measured_max_abs_error == 0.0
    assert measurement.is_deterministic is True
    assert len(measurement.closure_reasons_failed) == 0


def test_hyper_sla_closure_failure_on_exceeded_latency():
    """
    Verify HYPER-SLA Engine: Fail-Closed enforcement when actual runtime
    exceeds declared application latency requirement.
    """
    sla = ApplicationSLA(
        workload_name="unrealistic_latency_sla",
        required_latency_ms=0.0001,  # Impossible 100ns requirement
        required_accuracy=1.0,
    )

    A = np.random.randn(100, 100).astype(np.float32)
    ref = A @ A
    execute_fn = lambda: A @ A

    engine = HyperSLAEngine()
    measurement = engine.evaluate_workload(sla, execute_fn, ref, repetitions=2)

    assert measurement.contract_closure is False
    assert len(measurement.closure_reasons_failed) > 0
    assert "Latency exceeded SLA" in measurement.closure_reasons_failed[0]


def test_four_master_metrics():
    """
    Verify the Four 100% Master Metrics and explicit declaration that
    PHYSICAL_NVIDIA_HARDWARE_PARITY is NOT_ESTABLISHED under local CPU/UHD constraints.
    """
    metrics = FourMasterMetrics(
        verified_semantic_elements=44,
        declared_semantic_elements=44,
        contracts_satisfied=10,
        contracts_tested=10,
        traceable_results=50,
        reported_results=50,
        sla_closures_passed=5,
        sla_closures_claimed=5,
    )

    d = metrics.to_dict()
    four = d["four_100_percent_metrics"]
    assert four["1_semantic_execution_coverage_pct"] == 100.0
    assert four["2_contract_correctness_pct"] == 100.0
    assert four["3_evidence_integrity_pct"] == 100.0
    assert four["4_contract_performance_closure_pct"] == 100.0
    assert d["physical_nvidia_hardware_parity"] == "NOT_ESTABLISHED"
