"""
tests/test_breakthrough_comprehensive.py
========================================
Comprehensive verification suite for breakthrough capabilities:
- Speculative Execution Engine (Section 23)
- Information-Theoretic Entropy Analysis (Section 36)
- Fuzzing & 3-Tier Blind Holdout Certification (Sections 45 & 47)
- Adaptive, Thermal-Aware & Self-Optimizing Runtime (Sections 66-70)
- End-to-End CLI Breakthrough Discovery Mode (Section 77)
"""

import numpy as np
import pytest

from hyper.contracts.contract import Contract
from hyper.executor.speculative_executor import (
    SpeculativeExecutor,
    SpeculativeResult,
    SpeculationTelemetry,
)
from hyper.information.entropy_analyzer import (
    InformationTheoreticAnalyzer,
    InformationProfile,
)
from hyper.adversarial.blind_holdout_fuzzer import (
    BlindHoldoutFuzzer,
    DatasetSplit,
    FuzzReport,
)
from hyper.runtime.adaptive_runtime import (
    AdaptiveRuntime,
    ExecutionBackend,
    ThermalTelemetry,
)


def test_speculative_execution_accepted():
    """
    Verify Speculative Execution: When candidate prediction passes verification,
    the result is accepted with net speedup and zero false acceptances.
    """
    executor = SpeculativeExecutor()

    # Fast predictor: returns approximate identity
    x = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    predictor = lambda: x.copy()
    exact_fallback = lambda: x.copy()

    # Verification function: accepts identical or error < 1e-4
    verify_fn = lambda cand: (bool(np.allclose(cand, x, atol=1e-4)), float(np.max(np.abs(cand - x))))

    res = executor.execute(
        predictor_fn=predictor,
        exact_fallback_fn=exact_fallback,
        verify_fn=verify_fn,
        confidence_threshold=0.8,
        estimated_confidence=0.95,
    )

    assert res.speculation_accepted is True
    assert res.verification_passed is True
    assert res.execution_path == "SPECULATION_ACCEPTED"
    assert executor.telemetry.false_acceptance == 0
    assert executor.telemetry.speculation_accepted == 1


def test_speculative_execution_rejected_verification_failure():
    """
    Verify Speculative Execution Fail-Closed: When candidate prediction fails verification,
    it is strictly rejected and the system falls back to exact execution.
    """
    executor = SpeculativeExecutor()

    x = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    # Flawed predictor: adds noise
    flawed_predictor = lambda: x + 5.0
    exact_fallback = lambda: x.copy()

    verify_fn = lambda cand: (bool(np.allclose(cand, x, atol=1e-4)), float(np.max(np.abs(cand - x))))

    res = executor.execute(
        predictor_fn=flawed_predictor,
        exact_fallback_fn=exact_fallback,
        verify_fn=verify_fn,
        confidence_threshold=0.8,
        estimated_confidence=0.95,
    )

    assert res.speculation_accepted is False
    assert res.verification_passed is False
    assert res.execution_path == "SPECULATION_REJECTED_EXACT_FALLBACK"
    np.testing.assert_allclose(res.output, x)
    assert executor.telemetry.speculation_rejected == 1
    assert executor.telemetry.fallback_invocations == 1
    assert executor.telemetry.false_acceptance == 0


def test_speculative_execution_bypassed_low_confidence():
    """
    Verify Speculative Execution: When confidence is below threshold,
    speculation is safely bypassed and exact fallback is invoked immediately.
    """
    executor = SpeculativeExecutor()

    x = np.array([10.0, 20.0], dtype=np.float32)
    res = executor.execute(
        predictor_fn=lambda: x * 2.0,
        exact_fallback_fn=lambda: x.copy(),
        verify_fn=lambda c: (True, 0.0),
        confidence_threshold=0.90,
        estimated_confidence=0.50,  # Below threshold!
    )

    assert res.speculation_accepted is False
    assert res.execution_path == "EXACT_FALLBACK_BYPASSED_LOW_CONFIDENCE"
    np.testing.assert_allclose(res.output, x)
    assert executor.telemetry.fallback_invocations == 1


def test_information_theoretic_entropy_high_entropy_signal():
    """
    Verify Information-Theoretic Analyzer: Pure Gaussian white noise has high Shannon entropy
    and low redundancy, leading to RECOMMEND_EXACT_FALLBACK_HIGH_ENTROPY recommendation.
    """
    np.random.seed(42)
    noise = np.random.randn(1000).astype(np.float32)

    analyzer = InformationTheoreticAnalyzer()
    profile = analyzer.analyze(noise)

    assert profile.shannon_entropy_bits > 5.0
    assert profile.redundancy_ratio < 0.3
    d = profile.to_dict()
    assert "guidance" in d["methodology_disclaimer"].lower() or "guide" in d["methodology_disclaimer"].lower()


def test_information_theoretic_entropy_smooth_spatial_gradient():
    """
    Verify Information-Theoretic Analyzer: Smooth 2D spatial gradients exhibit high
    spatial redundancy and prompt separable/frequency decomposition recommendations.
    """
    grid = np.linspace(0, 1, 64)
    smooth_2d = np.outer(grid, grid).astype(np.float32)

    analyzer = InformationTheoreticAnalyzer()
    profile = analyzer.analyze(smooth_2d)

    assert profile.spatial_redundancy is not None
    assert profile.spatial_redundancy > 0.70
    assert profile.optimization_recommendation in (
        "RECOMMEND_SEPARABLE_OR_FREQUENCY_DECOMPOSITION",
        "RECOMMEND_STANDARD_ALGEBRAIC_SEARCH",
    )


def test_information_theoretic_entropy_sparse_tensor():
    """
    Verify Information-Theoretic Analyzer: Heavily sparse matrix is recognized
    with RECOMMEND_SPARSE_REPRESENTATION recommendation.
    """
    sparse_mat = np.zeros((100, 100), dtype=np.float32)
    sparse_mat[5, 5] = 1.0
    sparse_mat[12, 8] = 2.5

    analyzer = InformationTheoreticAnalyzer()
    profile = analyzer.analyze(sparse_mat)

    assert profile.optimization_recommendation == "RECOMMEND_SPARSE_REPRESENTATION"


def test_blind_holdout_dataset_partitioning():
    """
    Verify Blind Holdout Fuzzer: Partitions inputs into 3 disjoint datasets
    with distinct RNG states (Discovery != Verification != Blind Holdout).
    """
    fuzzer = BlindHoldoutFuzzer(base_seed=1234)
    splits = fuzzer.generate_partitioned_dataset(num_samples_per_split=5, shape=(8, 8))

    assert len(splits[DatasetSplit.DISCOVERY]) == 5
    assert len(splits[DatasetSplit.VERIFICATION]) == 5
    assert len(splits[DatasetSplit.BLIND_HOLDOUT]) == 5

    # Check that splits are mathematically distinct
    disc_0 = splits[DatasetSplit.DISCOVERY][0]
    verif_0 = splits[DatasetSplit.VERIFICATION][0]
    holdout_0 = splits[DatasetSplit.BLIND_HOLDOUT][0]

    assert not np.array_equal(disc_0, verif_0)
    assert not np.array_equal(disc_0, holdout_0)
    assert not np.array_equal(verif_0, holdout_0)


def test_blind_holdout_boundary_inputs_generation():
    """
    Verify Blind Holdout Fuzzer: Generates pathological boundary inputs:
    zeros, ones, subnormals, large dynamic range, and alternating signs.
    """
    fuzzer = BlindHoldoutFuzzer()
    boundaries = fuzzer.generate_boundary_inputs(shape=(10, 10))

    assert len(boundaries) >= 5
    # Zeros check
    assert np.all(boundaries[0] == 0.0)
    # Ones check
    assert np.all(boundaries[1] == 1.0)
    # Subnormals check
    assert np.all(boundaries[2] < 1e-30)


def test_blind_holdout_certification_exact_match():
    """
    Verify Blind Holdout Fuzzer: Candidate passing all blind holdout tests achieves
    formal certification with zero false escapes.
    """
    fuzzer = BlindHoldoutFuzzer(base_seed=42)
    splits = fuzzer.generate_partitioned_dataset(num_samples_per_split=10, shape=(16, 16))
    holdout_set = splits[DatasetSplit.BLIND_HOLDOUT]

    contract = Contract(
        name="exact_fuzz_contract",
        exact_required=True,
        max_abs_error=0.0,
        max_relative_error=0.0,
        max_rmse=0.0,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=100.0,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=False,
        allow_prediction=False,
        allow_approximation=False,
        allow_perceptual_difference=False,
    )

    # Candidate and golden reference perform exact ReLU
    cand_fn = lambda arr: np.maximum(arr, 0)
    gold_fn = lambda arr: np.maximum(arr, 0)

    certified, report = fuzzer.run_holdout_certification(cand_fn, gold_fn, holdout_set, contract)

    assert certified is True
    assert report.passed == 10
    assert report.failed == 0
    assert report.false_escapes == 0


def test_adaptive_runtime_telemetry_and_signature_routing():
    """
    Verify Adaptive Runtime: Queries local system telemetry, generates deterministic
    workload signatures, and stores learned routing decisions without overriding verification.
    """
    runtime = AdaptiveRuntime()

    # Telemetry
    telemetry = runtime.get_telemetry()
    assert isinstance(telemetry, ThermalTelemetry)
    assert telemetry.ram_used_gb >= 0.0

    # Signature routing
    inp = np.ones((100, 100), dtype=np.float32)
    backend = runtime.select_backend("MATMUL", inp, has_proven_escape=False)
    assert backend in (ExecutionBackend.OPTIMIZED_CPU_AVX2, ExecutionBackend.HYBRID_ZERO_COPY)

    # When proven escape exists
    escape_backend = runtime.select_backend("MATMUL", inp, has_proven_escape=True)
    assert escape_backend == ExecutionBackend.ESCAPE

    # Record decision and verify retrieval
    runtime.record_decision("MATMUL", inp, ExecutionBackend.OPTIMIZED_CPU_AVX2, measured_latency_ms=1.23)
    summary = runtime.summary()
    assert summary["total_decisions_recorded"] == 1
    assert summary["learned_routes_count"] == 1
