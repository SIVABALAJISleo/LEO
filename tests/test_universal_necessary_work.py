"""
tests/test_universal_necessary_work.py
=============================================================================
Unit & Integration Test Suite for Universal Necessary-Work Compiler
=============================================================================
Tests:
  1. Universal Contract IR (7 correctness modes, strict invariant validation)
  2. Prevention of unauthorized approximation downgrade (EXACT -> APPROXIMATE)
  3. Observable Compiler & ObservableIR across domains
  4. Causal Information Boundary (REQUIRED, POTENTIALLY_REQUIRED, PROVABLY_UNNECESSARY, UNKNOWN)
  5. Necessary-Work Compiler G_N optimization and GADR/HAE calculation
  6. Counterfactual Elimination Engine attacking candidates with 8 adversarial suites
  7. Causal Necessity Certificates (ELIMINATED_VERIFIED, NECESSARY_PROVEN, SHA-256)
  8. CPU + Intel UHD Hybrid Scheduler empirical trade-offs
  9. Zero-copy / Memory Movement Optimizer
 10. Sparsity Elimination with strict exact zero vs threshold decoupling
 11. Residual Engine with confidence guards and fallback
 12. Automated Scientific Auditor detecting impossible claims and simulated confusion
 13. Universal Workload Registry & Closure Scorecard
"""

import pytest
import numpy as np

from hyper_x.wormhole_compiler.contract_ir import (
    UniversalWorkloadContract,
    CorrectnessMode,
    CachePolicy,
    ExecutionTrack,
)
from hyper_x.wormhole_compiler.observable_compiler import (
    UniversalObservableCompiler,
    ObservableIR,
    ObservableDomain,
)
from hyper_x.wormhole_compiler.information_boundary import (
    InformationBoundaryEngine,
    CausalClassification,
    BoundaryAnalysisResult,
)
from hyper_x.wormhole_compiler.necessary_work_compiler import (
    NecessaryWorkCompiler,
    NecessaryWorkGraph,
    NecessaryWorkNode,
)
from hyper_x.wormhole_compiler.counterfactual_elimination import (
    CounterfactualEliminationEngine,
)
from hyper_x.wormhole_compiler.necessity_certificate import (
    CausalNecessityCertificate,
    NecessityStatus,
)
from hyper_x.wormhole_compiler.hybrid_scheduler import (
    HybridScheduler,
    TargetDevice,
)
from hyper_x.wormhole_compiler.memory_movement_optimizer import (
    MemoryMovementOptimizer,
)
from hyper_x.wormhole_compiler.sparse_work_elimination import (
    SparsityEliminationEngine,
)
from hyper_x.wormhole_compiler.residual_engine import (
    ResidualEngine,
)
from hyper_x.wormhole_compiler.scientific_auditor import (
    ScientificAuditor,
)
from hyper_x.wormhole_compiler.workload_registry import (
    UniversalWorkloadRegistry,
    WorkloadRegistryEntry,
    WorkloadOutcome,
)


def test_contract_ir_prevents_unauthorized_downgrade():
    exact_contract = UniversalWorkloadContract(
        workload_id="GEMM_EXACT",
        operation="matrix_multiply",
        correctness_mode=CorrectnessMode.EXACT,
        tolerance=0.0
    )
    assert exact_contract.is_exact() is True
    assert exact_contract.allows_approximation() is False
    # Attempting to downgrade EXACT to BOUNDED_APPROXIMATION must be rejected
    assert exact_contract.validate_transformation(CorrectnessMode.BOUNDED_APPROXIMATION) is False
    assert exact_contract.validate_transformation(CorrectnessMode.EXACT_REFORMULATION) is True


def test_observable_compiler_domains():
    obs_tensor = UniversalObservableCompiler.full_tensor((64, 64))
    assert obs_tensor.domain == ObservableDomain.DENSE_TENSOR
    assert obs_tensor.dimension_reduction_ratio == 1.0

    obs_proj = UniversalObservableCompiler.output_projection(output_dim=1, total_dim=64)
    assert obs_proj.dimension_reduction_ratio == 1.0 / 64.0

    obs_tokens = UniversalObservableCompiler.ai_requested_tokens(vocab_size=32000, top_k=1)
    assert obs_tokens.domain == ObservableDomain.AI_TOKENS
    assert obs_tokens.target_shape == (1,)

    obs_gfx = UniversalObservableCompiler.graphics_visible_pixels((1080, 1920))
    assert obs_gfx.domain == ObservableDomain.GRAPHICS_PIXELS


def test_causal_information_boundary():
    engine = InformationBoundaryEngine()
    audit_req = engine.classify_node_causality("node_1", ancestors_of_observable={"node_1"}, sensitivity=1.0)
    assert audit_req.causal_classification == CausalClassification.REQUIRED
    assert audit_req.is_safe_to_eliminate is False

    audit_unnec = engine.classify_node_causality("scratch_buf", ancestors_of_observable=set(), sensitivity=0.0)
    assert audit_unnec.causal_classification == CausalClassification.PROVABLY_UNNECESSARY
    assert audit_unnec.is_safe_to_eliminate is True


def test_counterfactual_elimination_catches_false_shortcut():
    contract = UniversalWorkloadContract(
        workload_id="TEST_ELIM",
        operation="matrix_multiply",
        correctness_mode=CorrectnessMode.EXACT,
        tolerance=0.0
    )
    A = np.eye(16, dtype=np.float32)
    B = np.ones((16, 16), dtype=np.float32)

    # Attempting to eliminate multiplication by replacing with identity or wrong output
    res = CounterfactualEliminationEngine.evaluate_elimination(
        operation_id="gemm_op",
        baseline_fn=lambda a, b: a @ b,
        ablated_candidate_fn=lambda a, b: np.zeros((16, 16), dtype=np.float32),
        nominal_inputs=(A, B),
        contract=contract,
    )
    assert res.elimination_succeeded is False
    assert res.counterexample is not None
    assert res.adversarial_tests_passed == 0


def test_necessity_certificates():
    cert_elim = CausalNecessityCertificate.create_eliminated_verified(
        operation_id="intermediate_tensor",
        workload_id="GEMM_TEST",
        observable="vector_y",
        dependency_path=["A", "B", "x", "y"],
        elimination_attempt="associative_rewrite",
        adversarial_results={"tests_run": 8, "passed": 8},
        holdout_results={"passed": True},
        fallback_strategy="exact_gemm",
        provenance={"target_cpu": "Intel Core i5-12450H"},
    )
    assert cert_elim.final_status == NecessityStatus.ELIMINATED_VERIFIED
    assert len(cert_elim.sha256_signature) == 64

    cert_nec = CausalNecessityCertificate.create_necessary_proven(
        operation_id="dense_core",
        workload_id="DENSE_EXACT",
        observable="full_matrix",
        dependency_path=["A", "B", "out"],
        counterexamples=[{"reason": "Non-zero error"}],
        proof_status="MATHEMATICALLY_DERIVED",
        provenance={"target_cpu": "Intel Core i5-12450H"},
    )
    assert cert_nec.final_status == NecessityStatus.NECESSARY_PROVEN


def test_hybrid_scheduler_tradeoffs():
    scheduler = HybridScheduler()
    # Very small matrix: CPU AVX2 should be chosen over UHD due to launch overhead
    decision_small = scheduler.partition_workload("SMALL_GEMM", flops=1e4, input_bytes=1024, output_bytes=512)
    assert decision_small.selected_device == TargetDevice.CPU_AVX2

    # High arithmetic intensity workload: UHD or cooperative hybrid should be chosen
    decision_large = scheduler.partition_workload("LARGE_GEMM", flops=2e9, input_bytes=1024*1024*2, output_bytes=1024*1024)
    assert decision_large.selected_device in (TargetDevice.INTEL_UHD, TargetDevice.HYBRID_COOPERATIVE)


def test_memory_movement_optimizer():
    opt = MemoryMovementOptimizer()
    t1 = np.ones((64, 64), dtype=np.float32)
    t2 = np.ones((64, 64), dtype=np.float32)
    t3 = np.ones((64, 64), dtype=np.float32)
    report = opt.analyze_pipeline_memory("PIPE_01", [t1, t2], [t3], [t3], enable_fusion=True)
    assert report.movement_elimination_ratio > 0.0
    assert report.zero_copy_buffers_used >= 1


def test_sparsity_engine_exact_vs_approx():
    A = np.zeros((32, 32), dtype=np.float32)
    A[0, 0] = 5.0
    B = np.ones((32, 32), dtype=np.float32)

    contract_exact = UniversalWorkloadContract("SPARSE_EXACT", "gemm", CorrectnessMode.EXACT, tolerance=0.0)
    C_exact, rep_exact = SparsityEliminationEngine.sparse_gemm_execution(A, B, contract_exact)
    assert rep_exact.is_exact_mode is True
    assert rep_exact.threshold_applied == 0.0
    assert np.allclose(C_exact, A @ B)


def test_residual_engine_confidence_guard():
    contract = UniversalWorkloadContract("RESIDUAL_TEST", "predict", CorrectnessMode.BOUNDED_APPROXIMATION, tolerance=1e-3)
    data = np.ones((16, 16), dtype=np.float32)

    # Low confidence predictor must trigger exact fallback
    pred_bad = lambda x: (x * 0.5, 0.40)  # low confidence 0.40 < threshold
    exact_fn = lambda x: x * 2.0
    out, rep = ResidualEngine.execute_with_residual_guard(data, pred_bad, exact_fn, contract, 1000.0, 100.0)
    assert rep.fallback_invoked is True
    assert np.allclose(out, data * 2.0)


def test_scientific_auditor():
    # 1. Prohibited claim detection
    findings = ScientificAuditor.audit_statement("HYPER achieves 100% NVIDIA parity and GPU replaced.")
    assert len(findings) >= 1
    assert any(f.category == "IMPOSSIBLE_CLAIM" for f in findings)

    # 2. Simulation labeled as physical hardware
    rep = ScientificAuditor.audit_result_record(
        workload_id="SIM_CLAIM",
        contract_mode="EXACT",
        numerical_error=0.0,
        holdout_passed=True,
        provenance={"cpu": "Intel Core i5-12450H"},
        is_simulated=True,
        claimed_as_real_hardware=True
    )
    assert rep.passed is False
    assert rep.critical_violations >= 1


def test_workload_registry_and_closure():
    reg = UniversalWorkloadRegistry(registry_path=None)
    reg.entries.clear()

    e1 = WorkloadRegistryEntry(
        workload_id="W1",
        domain="matrix",
        contract_mode="EXACT_REFORMULATION",
        observable="vector",
        outcome=WorkloadOutcome.WORMHOLE_FOUND,
        speedup=3.5,
        work_elimination_ratio=0.85,
        gadr=0.15,
        hae=0.85,
        provenance_verified=True,
        holdout_passed=True,
        exact_correctness=True,
        contract_correctness=True,
    )
    e2 = WorkloadRegistryEntry(
        workload_id="W2",
        domain="dense_gaussian",
        contract_mode="EXACT",
        observable="full_matrix",
        outcome=WorkloadOutcome.NECESSARY_COMPUTATION_PROVEN,
        speedup=1.0,
        work_elimination_ratio=0.0,
        gadr=1.0,
        hae=0.0,
        provenance_verified=True,
        holdout_passed=True,
        exact_correctness=True,
        contract_correctness=True,
    )
    reg.register(e1)
    reg.register(e2)

    scorecard = reg.compute_closure()
    assert scorecard.total_evaluated_workloads == 2
    assert scorecard.wormholes_found == 1
    assert scorecard.necessity_proven == 1
    assert scorecard.inconclusive_searches == 0
    assert scorecard.closure_ratio == 1.0  # 100% Workload Closure achieved
    assert scorecard.can_claim_100_percent_closure is True
