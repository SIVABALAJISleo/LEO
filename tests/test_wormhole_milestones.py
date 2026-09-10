"""
tests/test_wormhole_milestones.py
=============================================================================
HYPER-X Wormhole Compiler Milestones 2-5 Verification Suite
=============================================================================
Tests:
  1. KernelSecuritySandbox (Phase 51): AST inspection, blocking RCE/dangerous calls.
  2. HardwareAdvantageMap (Phases 15-21): Analytical GADR & HAE metrics.
  3. EGraphSaturationEngine (Phase 10): HardwareCostVector and Pareto extraction.
  4. StrictParityScorecard (Phase 32): Full 11-gate conjunctive evaluation.
  5. UniversalDomainAdapters (Phases 22-25): Real physical compute across 6 domains.
  6. CompetitiveCoverageEngine (Phase 37): 8-dimension scorecard & audit integrity.
"""

import pytest
import numpy as np
import time
from pathlib import Path

from hyper_x.wormhole_compiler.security_sandbox import (
    KernelSecuritySandbox,
    SecuritySandboxViolation,
)
from hyper_x.wormhole_compiler.hardware_advantage_map import (
    HardwareAdvantageMap,
)
from hyper_x.wormhole_compiler.egraph_search import (
    EqualitySaturationEngine,
    HardwareCostVector,
)
from hyper_x.wormhole_compiler.parity_gates import (
    ParityEvaluator,
    StrictParityScorecard,
)
from hyper_x.wormhole_compiler.contract_ir import (
    UniversalWorkloadContract,
    CorrectnessMode,
    CachePolicy,
)
from hyper_x.wormhole_compiler.schemas import (
    WorkloadContract,
    CorrectnessRequirement,
    ExecutionTrack,
    PowerTelemetryType,
)
from hyper_x.wormhole_compiler.domain_adapters_universe import (
    DenseLinearAlgebraAdapter,
    AIInferenceAdapter,
    GraphicsTemporalAdapter,
    ScientificComputingAdapter,
    DatabaseProcessingAdapter,
    CryptographyAdapter,
)
from hyper_x.wormhole_compiler.workload_registry import (
    UniversalWorkloadRegistry,
    WorkloadRegistryEntry,
    WorkloadOutcome,
)


def test_security_sandbox_ast_blocking():
    """Verify that KernelSecuritySandbox strictly blocks dangerous operations."""
    sandbox = KernelSecuritySandbox()

    # Blocked imports
    assert not sandbox.inspect_code("import os")[0]
    assert not sandbox.inspect_code("import sys, subprocess")[0]
    assert not sandbox.inspect_code("from shutil import rmtree")[0]
    assert not sandbox.inspect_code("import socket")[0]

    # Blocked built-ins
    assert not sandbox.inspect_code("eval('1 + 1')")[0]
    assert not sandbox.inspect_code("exec('x = 10')")[0]
    assert not sandbox.inspect_code("open('/etc/passwd', 'r')")[0]
    assert not sandbox.inspect_code("__import__('os')")[0]

    # Blocked dunder attributes
    assert not sandbox.inspect_code("x = ().__class__.__bases__[0].__subclasses__()")[0]

    # Safe mathematical operations allowed
    is_safe, violations = sandbox.inspect_code("y = np.dot(A, B) + 1.0")
    assert is_safe
    assert len(violations) == 0

    # Safe execution execution report
    rep = sandbox.execute_safe_string("res = 40 + 2")
    assert rep.is_safe
    assert rep.output["res"] == 42


def test_hardware_advantage_map_analytical():
    """Verify formal analytical GADR and HAE calculations."""
    res = HardwareAdvantageMap.calculate_gadr_and_hae(
        nominal_flops=1e9,
        optimized_flops=2e8,
        nominal_bytes_moved=1e8,
        optimized_bytes_moved=3e7,
        domain="dense_linear_algebra"
    )
    gadr = res["gadr"]
    hae = res["hae"]

    assert 0.0 <= gadr <= 1.0
    assert 0.0 <= hae <= 1.0
    assert np.isclose(gadr + hae, 1.0)
    assert res["work_elimination_ratio"] == 0.8
    assert res["memory_movement_elimination_ratio"] == 0.7
    assert "scientific_disclaimer" in res


def test_egraph_hardware_cost_vector_and_pareto():
    """Verify multi-attribute hardware-aware cost extraction and Pareto frontiers in egraphs."""
    engine = EqualitySaturationEngine(exact_only=True)
    cid = engine.add_expression("(A @ B) @ C")
    engine.saturate(iterations=2)

    expr, vec = engine.extract_cheapest_vector(cid)
    assert isinstance(vec, HardwareCostVector)
    assert vec.flops > 0
    assert vec.memory_bytes > 0

    pareto = engine.extract_pareto_optimal(cid)
    assert len(pareto) >= 1
    for p_expr, p_vec in pareto:
        assert isinstance(p_vec, HardwareCostVector)


def test_parity_gates_11_gate_conjunctive():
    """Verify that all 11 gates are evaluated and overall passes only conjunctively."""
    contract = WorkloadContract(
        workload_id="TEST_WORKLOAD_11G",
        operation="test_op",
        input_shape=(10, 10),
        output_shape=(10, 10),
        correctness=CorrectnessRequirement.NUMERICAL_TOLERANCE,
        tolerance=1e-3,
        latency_slo_ms=50.0,
        memory_limit_mb=128.0
    )

    # All passing -> Overall pass
    card_pass = ParityEvaluator.evaluate(
        contract=contract,
        candidate_latency_ms=10.0,
        reference_latency_ms=25.0,
        numerical_error=1e-4,
        nominal_reference_flops=1000,
        actual_necessary_flops=500,
        memory_used_mb=32.0,
        provenance_valid=True,
        holdout_passed=True,
        adversarial_passed=True,
        baseline_integrity_passed=True,
        candidate_output=np.zeros((10, 10)),
        reference_output=np.zeros((10, 10))
    )
    assert card_pass.baseline_integrity_gate
    assert card_pass.exact_parity_gate is False  # numerical error > 0.0
    assert card_pass.numerical_parity_gate
    assert card_pass.functional_parity_gate
    assert card_pass.contract_parity_gate
    assert card_pass.application_parity_gate
    assert card_pass.performance_parity_gate
    assert card_pass.resource_parity_gate
    assert card_pass.provenance_gate
    assert card_pass.adversarial_gate
    assert card_pass.holdout_gate
    assert card_pass.overall_conjunctive_gate is True

    # If adversarial fails -> Overall must fail
    card_adv_fail = ParityEvaluator.evaluate(
        contract=contract,
        candidate_latency_ms=10.0,
        reference_latency_ms=25.0,
        numerical_error=1e-4,
        nominal_reference_flops=1000,
        actual_necessary_flops=500,
        memory_used_mb=32.0,
        provenance_valid=True,
        holdout_passed=True,
        adversarial_passed=False,  # FAIL
        baseline_integrity_passed=True,
        candidate_output=np.zeros((10, 10)),
        reference_output=np.zeros((10, 10))
    )
    assert card_adv_fail.adversarial_gate is False
    assert card_adv_fail.overall_conjunctive_gate is False


def test_domain_adapters_universe_all_six():
    """Verify physical execution and contract consistency across all 6 domain adapters."""
    # Domain 1: GEMM
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    c1, _ = DenseLinearAlgebraAdapter.build_gemm_contract(32, 32, 32)
    ref1, lat_ref1 = DenseLinearAlgebraAdapter.execute_reference(A, B)
    cand1, lat_cand1, _ = DenseLinearAlgebraAdapter.execute_wormhole_candidate(A, B, c1)
    assert lat_ref1 >= 0.0
    assert lat_cand1 >= 0.0
    assert cand1.shape == (32, 32)

    # Domain 2: AI Attention
    Q = np.random.randn(16, 16).astype(np.float32)
    K = np.random.randn(16, 16).astype(np.float32)
    V = np.random.randn(16, 16).astype(np.float32)
    c2, _ = AIInferenceAdapter.build_attention_contract(16, 16)
    ref2, _ = AIInferenceAdapter.execute_reference(Q, K, V)
    cand2, _, _ = AIInferenceAdapter.execute_wormhole_candidate(Q, K, V, c2)
    assert cand2.shape == (16, 16)

    # Domain 3: Graphics Temporal
    frame = np.random.randn(32, 32).astype(np.float32)
    c3, _ = GraphicsTemporalAdapter.build_frame_contract((32, 32))
    ref3, _ = GraphicsTemporalAdapter.execute_reference(frame)
    cand3, _, _ = GraphicsTemporalAdapter.execute_wormhole_candidate(frame, frame, c3)
    assert cand3.shape == (32, 32)

    # Domain 4: Scientific PDE Stencil
    grid = np.random.randn(16, 16).astype(np.float32)
    ref4, _ = ScientificComputingAdapter.execute_reference(grid, steps=2)
    cand4, _, _ = ScientificComputingAdapter.execute_wormhole_candidate(grid, steps=2)
    assert cand4.shape == (16, 16)

    # Domain 5: DB Query Filtering & Sum
    vals = np.random.randn(1000).astype(np.float32)
    filter_col = np.random.uniform(0, 100, 1000).astype(np.float32)
    ref5, _ = DatabaseProcessingAdapter.execute_reference(vals, filter_col, threshold=50.0)
    cand5, _, _ = DatabaseProcessingAdapter.execute_wormhole_candidate(vals, filter_col, threshold=50.0)
    assert np.isclose(ref5, cand5, atol=1e-5)

    # Domain 6: Cryptography SHA-256 Merkle Root
    leaves = [b"leaf_0", b"leaf_1", b"leaf_2", b"leaf_3"]
    ref6, _ = CryptographyAdapter.execute_reference(leaves)
    cand6, _, _ = CryptographyAdapter.execute_wormhole_candidate(leaves)
    assert ref6 == cand6
    assert len(ref6) == 64


def test_competitive_coverage_engine(tmp_path: Path):
    """Verify that 8D competitive coverage accurately captures closure and denies false passes."""
    reg_path = tmp_path / "test_reg.json"
    reg = UniversalWorkloadRegistry(registry_path=reg_path)

    # Empty registry
    cov0 = reg.compute_competitive_coverage()
    assert cov0.total_evaluated_workloads == 0
    assert cov0.audit_passed is False

    # 1 wormhole + 1 proven
    reg.register(WorkloadRegistryEntry(
        workload_id="W1", domain="gemm", contract_mode="EXACT", observable="out",
        outcome=WorkloadOutcome.WORMHOLE_FOUND, speedup=2.5, work_elimination_ratio=0.8,
        gadr=0.2, hae=0.8, provenance_verified=True, holdout_passed=True,
        exact_correctness=True, contract_correctness=True
    ))
    reg.register(WorkloadRegistryEntry(
        workload_id="W2", domain="gemm", contract_mode="EXACT", observable="out",
        outcome=WorkloadOutcome.NECESSARY_COMPUTATION_PROVEN, speedup=1.0, work_elimination_ratio=0.0,
        gadr=1.0, hae=0.0, provenance_verified=True, holdout_passed=True,
        exact_correctness=True, contract_correctness=True
    ))

    cov1 = reg.compute_competitive_coverage(universe_target=2)
    assert cov1.closure_ratio == 1.0
    assert cov1.inconclusive_searches == 0
    assert cov1.audit_passed is True
    assert cov1.exact_coverage == 1.0

    # Add an inconclusive search -> audit_passed MUST become False!
    reg.register(WorkloadRegistryEntry(
        workload_id="W3", domain="gemm", contract_mode="APPROX", observable="out",
        outcome=WorkloadOutcome.SEARCH_INCONCLUSIVE, speedup=1.0, work_elimination_ratio=0.0,
        gadr=1.0, hae=0.0, provenance_verified=False, holdout_passed=False,
        exact_correctness=False, contract_correctness=False
    ))
    cov2 = reg.compute_competitive_coverage(universe_target=3)
    assert cov2.inconclusive_searches == 1
    assert cov2.audit_passed is False
    assert cov2.closure_ratio == 2.0 / 3.0
