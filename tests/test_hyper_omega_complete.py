"""
tests/test_hyper_omega_complete.py
==================================
Comprehensive automated test suite for HYPER-Ω:
- ExternalReferenceEngine
- ExternalEquivalenceVerifier
- BenchmarkIntegrityGuard
- CounterexampleRegistry
- ResearchDiscoveryAgent
- HyperOmegaRunner End-to-End
"""

import os
import sys
import numpy as np
import pytest

# Ensure root directory in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper_x.reference_engine import ExternalReferenceEngine
from hyper_x.equivalence_verifier import ExternalEquivalenceVerifier, EquivalenceMode, VerificationVerdict
from hyper_x.integrity_guard import BenchmarkIntegrityGuard
from hyper_x.counterexample_registry import CounterexampleRegistry, FailureClass
from hyper_x.research_agent import ResearchDiscoveryAgent, BarrierClassification
from hyper_x.omega_runner import HyperOmegaRunner, OmegaRunConfig


def test_reference_engine_isolation():
    ref_engine = ExternalReferenceEngine()
    x = np.ones((10, 10), dtype=np.float32)
    y = x * 2.0
    manifest = ref_engine.register_reference(
        workload_id="TEST_REF",
        input_data=x,
        output_data=y,
        reference_latency_ms=5.0,
        nominal_operations=100.0,
        nominal_memory_bytes=400.0,
    )
    assert manifest.input_hash is not None
    assert manifest.output_hash is not None
    assert ref_engine.get_manifest("TEST_REF") is not None
    # Verifier access only
    ref_out = ref_engine.get_reference_output_for_verification("TEST_REF")
    assert np.array_equal(ref_out, y)


def test_equivalence_verifier_fail_closed():
    a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    b = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    c = np.array([1.0, 2.0, 3.5], dtype=np.float32)

    # Identical arrays should pass exact bitwise
    rep_pass = ExternalEquivalenceVerifier.verify("TEST", a, b, EquivalenceMode.EXACT_BITWISE)
    assert rep_pass.verdict == VerificationVerdict.PASS
    assert rep_pass.is_bitwise_identical

    # Different arrays must fail exact bitwise and fail numerical if tolerance exceeded
    rep_fail = ExternalEquivalenceVerifier.verify(
        "TEST", a, c, EquivalenceMode.NUMERICALLY_EQUIVALENT, rel_tolerance=1e-3, abs_tolerance=1e-3
    )
    assert rep_fail.verdict == VerificationVerdict.FAIL
    assert rep_fail.max_absolute_error > 0.1


def test_integrity_guard_anti_fraud():
    # Candidate with hardcoded speedup should be caught
    def suspicious_fn(x):
        speedup = 2.15
        return x

    def clean_fn(x):
        return x * 2.0

    audit_bad = BenchmarkIntegrityGuard.audit_candidate_callable(suspicious_fn)
    assert not audit_bad.is_valid
    assert len(audit_bad.violations) > 0

    audit_good = BenchmarkIntegrityGuard.audit_candidate_callable(clean_fn)
    assert audit_good.is_valid


def test_counterexample_registry_learning():
    registry = CounterexampleRegistry()
    assert not registry.is_transformation_disproven("low_rank_svd", "random_dense_gemm")

    # Record a failure
    registry.record_counterexample(
        workload_class="random_dense_gemm",
        failure_mode=FailureClass.INSUFFICIENT_STRUCTURE,
        candidate_id="svd_candidate",
        transformation_name="low_rank_svd",
        input_hash="hash123",
        expected_output_hash="exp123",
        actual_output_hash="act123",
        numerical_error=0.45,
        hardware="CPU",
        environment="Win11",
        reproducibility_command="repro",
        structural_conditions={"rank": "full"},
    )

    # Now it should be recorded as disproven under those conditions
    assert registry.is_transformation_disproven(
        "low_rank_svd", "random_dense_gemm", {"rank": "full"}
    )


def test_research_agent_hypothesis():
    registry = CounterexampleRegistry()
    agent = ResearchDiscoveryAgent(registry)
    rec = registry.record_counterexample(
        workload_class="gemm",
        failure_mode=FailureClass.MEMORY_BOUND,
        candidate_id="cand1",
        transformation_name="dense_tiling",
        input_hash="h1",
        expected_output_hash="h2",
        actual_output_hash="h3",
        numerical_error=0.0,
        hardware="CPU",
        environment="Win11",
        reproducibility_command="repro",
    )
    barrier = agent.classify_barrier(rec)
    assert barrier == BarrierClassification.MEMORY_DEPENDENT

    hyp = agent.propose_hypothesis(barrier, "gemm", "cand1", {})
    assert hyp.hypothesis_id.startswith("HYP_MEM_")
    assert "DRAM" in hyp.hypothesis or "bandwidth" in hyp.why


def test_hyper_omega_runner_e2e():
    runner = HyperOmegaRunner()
    config = OmegaRunConfig(
        workload_id="TEST_WORKLOAD_E2E",
        equivalence_mode=EquivalenceMode.NUMERICALLY_EQUIVALENT,
        rel_tolerance=1e-4,
        abs_tolerance=1e-4,
        adversarial_samples=2,
        holdout_samples=2,
    )

    def ref_fn(x):
        return x * 3.0 + 1.0

    def cand_fn(x):
        return x * 3.0 + 1.0

    x_init = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    res = runner.run_workload(
        config=config,
        canonical_input=x_init,
        reference_fn=ref_fn,
        candidate_fn=cand_fn,
        adversarial_generator=lambda s: np.array([float(s), float(s + 1)], dtype=np.float32),
        holdout_generator=lambda s: np.array([float(s * 2)], dtype=np.float32),
    )

    assert res.status == "VERIFIED"
    assert res.certificate.certificate_hash != ""
    assert res.equivalence_report.verdict == VerificationVerdict.PASS
    assert res.integrity_audit.is_valid


def test_exact_reuse_engine():
    from hyper_x.cache.exact_reuse import ExactReuseEngine
    cache = ExactReuseEngine()
    arr = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    out = arr * 5.0

    # Cold lookup
    res_cold = cache.lookup(arr)
    assert not res_cold.is_hit
    assert res_cold.classification == "CACHE_MISS"

    # Store
    cache.store(arr, out, original_compute_latency_ms=4.5)

    # Warm lookup
    res_warm = cache.lookup(arr)
    assert res_warm.is_hit
    assert res_warm.classification == "COMPUTATION_AVOIDED_BY_EXACT_REUSE"
    assert res_warm.computation_avoided_ms == 4.5
    assert np.array_equal(res_warm.data, out)


def test_observable_and_output_directed():
    from hyper_x.info_boundary.observable_extractor import ObservableExtractor
    from hyper_x.info_boundary.output_directed import OutputDirectedEngine

    spec = ObservableExtractor.extract_from_contract(
        workload_id="TRACE_TEST",
        contract={"mode": "TRACE"},
        nominal_output_shape=(10, 10),
    )
    assert spec.observed_fraction == 0.1

    nodes = [
        {"id": "op_diag", "name": "diagonal_dot", "flops": 100.0, "is_off_diagonal": False},
        {"id": "op_off1", "name": "off_diag_1", "flops": 100.0, "is_off_diagonal": True},
        {"id": "op_off2", "name": "off_diag_2", "flops": 100.0, "is_off_diagonal": True},
    ]

    report = OutputDirectedEngine.slice_computation("TRACE_TEST", spec, nodes)
    assert report.total_operations == 3
    assert report.retained_operations == 1
    assert report.eliminated_operations == 2
    assert report.flops_saved_ratio > 0.6


def test_delta_engine_incremental():
    from hyper_x.delta.delta_engine import DeltaEngine
    delta_eng = DeltaEngine(tolerance=1e-3)

    frame1 = np.zeros((64, 64), dtype=np.float32)
    frame2 = np.zeros((64, 64), dtype=np.float32)
    # Modify only a small 10x10 corner
    frame2[0:10, 0:10] = 5.0

    def kernel(x):
        return x * 2.0

    out1, rep1 = delta_eng.compute_incremental("DIFF_TEST", frame1, kernel)
    assert not rep1.is_incremental  # First frame cold start

    out2, rep2 = delta_eng.compute_incremental("DIFF_TEST", frame2, kernel)
    assert rep2.is_incremental
    assert rep2.computation_saved_ratio > 0.5
    assert np.array_equal(out2[0:10, 0:10], frame2[0:10, 0:10] * 2.0)


def test_lossless_speculative():
    from hyper_x.prediction.lossless_speculative import LosslessSpeculativeEngine
    draft = [10, 20, 30, 40]
    # Target only agrees with first two
    def verifier(ctx):
        return [10, 20, 99, 88]

    res = LosslessSpeculativeEngine.verify_and_accept(draft, verifier, [])
    assert res.accepted_tokens == [10, 20]
    assert res.rejected_tokens == [30, 40]
    assert res.accepted_count == 2
    assert res.is_lossless


def test_four_parity_tracks():
    from hyper_x.verification.four_parity_tracks import FourParityEvaluator
    scorecard = FourParityEvaluator.evaluate(
        workload_id="GEMM_PARITY",
        is_same_algorithm=False,
        is_exact=True,
        ref_flops=1e9,
        cand_flops=5e8,
        ref_bytes=1e7,
        cand_bytes=5e6,
        contract_satisfied=True,
        quality_passed=True,
        latency_passed=True,
    )
    # Track 1 must be NO_HARDWARE_PARITY
    assert scorecard.track1_hardware.verdict == "NO_HARDWARE_PARITY"
    assert not scorecard.track1_hardware.physically_reproduces_gpu
    # Track 2 is DIFFERENT_COMPUTATION
    assert scorecard.track2_same_computation.verdict == "DIFFERENT_COMPUTATION"
    # Track 3 is VERIFIED_REDUCED_WORK
    assert scorecard.track3_reduced_computation.verdict == "VERIFIED_REDUCED_WORK"
    assert scorecard.track3_reduced_computation.operation_reduction_pct == 50.0
    # Track 4 is PASS
    assert scorecard.track4_contract_parity.verdict == "PASS"


def test_fallback_engine():
    from hyper_x.fallback.engine import FallbackEngine

    def failing_candidate(x):
        raise RuntimeError("Kernel crashed")

    def fallback_candidate(x):
        return x + 10

    res, meta = FallbackEngine.execute_with_fallback(failing_candidate, fallback_candidate, 5)
    assert res == 15
    assert meta["fallback_engaged"]
    assert meta["pathway"] == "TRUSTED_FALLBACK"
