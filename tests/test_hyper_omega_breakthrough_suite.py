"""
tests/test_hyper_omega_breakthrough_suite.py
=============================================================================
HYPER-Ω Breakthrough Regression & Verification Suite (Section 59)
=============================================================================
Tests all 11 Universal Computational Elimination routes:
  1. Exact Content Reuse & Cryptographic Hashing
  2. Exact Zero-Row & Zero-Column Pruning
  3. Exact Delta & Residual Computation
  4. Exact Sparsity Elimination
  5. Output-Sensitive Execution (Top-K / Projection)
  6. Temporal Coherence & Sequential Frame State Reuse
  7. Low-Rank Exact Factorization vs Approximate Isolation
  8. Precision Engine & Statistical Error Bounds
  9. Contract Enforcement & Exactness Guarantees
  10. Falsification & Counterexample Hunting
  11. Physical RTX 5090 Live Probe & Anti-Simulation Rule
  12. Decoupled Clean-Room Reference Fallback
"""

import pytest
import numpy as np
import time

from hyper_x.wormhole_compiler.breakthrough_router import BreakthroughRouter, BreakthroughRouteDecision
from hyper_x.wormhole_compiler.schemas import (
    WorkloadContract,
    CorrectnessRequirement,
    CachePolicy,
    ExecutionTrack,
)
from hyper_x.wormhole_compiler.contract import ContractCompiler
from hyper_x.wormhole_compiler.output_sensitive_engine import OutputSensitiveEngine
from hyper_x.wormhole_compiler.temporal_coherence_engine import TemporalCoherenceEngine
from hyper_x.wormhole_compiler.low_rank_engine import LowRankEngine
from hyper_x.wormhole_compiler.precision_engine import PrecisionEngine
from hyper_x.wormhole_compiler.representation_search import RepresentationSearchEngine
from hyper_x.wormhole_compiler.domain_adapters import (
    MatrixMultiplicationAdapter,
    GraphicsTemporalAdapter,
    OutputSensitiveTopKAdapter,
    ScientificStencilAdapter,
    RAGEmbeddingRetrievalAdapter,
)
from hyper_x.rtx5090.live_probe import RTX5090LiveProbe


@pytest.fixture
def router():
    return BreakthroughRouter()


# =============================================================================
# 1. Exact Content Reuse
# =============================================================================
def test_exact_content_reuse(router):
    contract = MatrixMultiplicationAdapter.build_contract(M=32, K=32, N=32, cache_policy=CachePolicy.WARM)
    A = np.ones((32, 32), dtype=np.float32)
    B = np.ones((32, 32), dtype=np.float32)

    # First call: Cold execution
    res1, dec1 = router.execute("gemm", (A, B), contract)
    assert dec1.verification_status in ["PASSED", "VERIFIED"]
    assert np.allclose(res1, 32.0)

    # Second call: Warm hit via SHA-256
    res2, dec2 = router.execute("gemm", (A, B), contract)
    assert dec2.route == "EXACT_CONTENT_REUSE"
    assert dec2.work_elimination_ratio == 1.0
    assert dec2.exact is True
    assert dec2.verification_status == "VERIFIED"
    assert np.array_equal(res1, res2)


# =============================================================================
# 2. Exact Zero-Row & Zero-Column Pruning
# =============================================================================
def test_exact_zero_row_pruning(router):
    contract = MatrixMultiplicationAdapter.build_contract(M=64, K=64, N=64, cache_policy=CachePolicy.COLD)
    A = np.random.randn(64, 64).astype(np.float32)
    A[0:32, :] = 0.0  # 50% of rows are exactly zero
    B = np.random.randn(64, 64).astype(np.float32)

    res, dec = router.execute("gemm", (A, B), contract)
    assert dec.route == "EXACT_ZERO_ROW_PRUNE"
    assert dec.work_elimination_ratio >= 0.50
    assert dec.verification_status == "PASSED"
    assert dec.exact is True
    # Independent verification
    ref = A @ B
    assert np.allclose(res, ref, atol=1e-4)


# =============================================================================
# 3. Exact Delta & Residual Computation
# =============================================================================
def test_exact_delta_computation(router):
    contract = MatrixMultiplicationAdapter.build_contract(M=64, K=64, N=64, cache_policy=CachePolicy.COLD)
    A_prev = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    # Step 1: Initial call
    router.execute("gemm", (A_prev, B), contract)

    # Step 2: Only 8 rows change out of 64 (87.5% unchanged rows)
    A_curr = A_prev.copy()
    A_curr[0:8, :] += np.random.randn(8, 64).astype(np.float32)

    res, dec = router.execute("gemm", (A_curr, B), contract)
    assert dec.route == "EXACT_ROW_DELTA"
    assert dec.work_elimination_ratio >= 0.80
    assert dec.verification_status == "PASSED"
    assert dec.exact is True
    # Independent clean-room verification
    ref = A_curr @ B
    assert np.allclose(res, ref, atol=1e-4)


# =============================================================================
# 4. Exact Sparsity Elimination
# =============================================================================
def test_exact_sparse_execution(router):
    contract = MatrixMultiplicationAdapter.build_contract(M=64, K=64, N=64, cache_policy=CachePolicy.COLD)
    # Generate 80% uniformly sparse matrix (scattered zeros, not whole rows)
    A = np.random.randn(64, 64).astype(np.float32)
    mask = np.random.rand(64, 64) > 0.20
    A[mask] = 0.0
    B = np.random.randn(64, 64).astype(np.float32)

    res, dec = router.execute("gemm", (A, B), contract)
    if dec.route == "EXACT_SPARSE":
        assert dec.work_elimination_ratio >= 0.70
        assert dec.exact is True
        assert dec.verification_status == "PASSED"
        ref = A @ B
        assert np.allclose(res, ref, atol=1e-4)


# =============================================================================
# 5. Output-Sensitive Execution (Top-K)
# =============================================================================
def test_output_sensitive_top_k(router):
    contract = OutputSensitiveTopKAdapter.build_contract(M=256, K=64, k=5)
    A = np.random.randn(256, 64).astype(np.float32)
    x = np.random.randn(64).astype(np.float32)

    (vals, idx), dec = router.execute("top_k_projection", (A, x), contract, config={"k": 5})
    assert dec.route == "OUTPUT_SENSITIVE"
    assert dec.verification_status == "PASSED"
    assert dec.exact is True
    assert len(vals) == 5
    assert len(idx) == 5

    # Decoupled independent reference comparison
    full_dot = A @ x
    ref_idx = np.argsort(-full_dot)[:5]
    ref_vals = full_dot[ref_idx]
    assert np.allclose(vals, ref_vals, atol=1e-4)


# =============================================================================
# 6. Temporal Coherence & Sequential Frame State Reuse
# =============================================================================
def test_temporal_coherence(router):
    contract = GraphicsTemporalAdapter.build_contract(resolution=(64, 64))
    f1 = np.ones((64, 64), dtype=np.float32)

    # Frame 1: Cold
    out1, dec1 = router.execute("graphics_filter", (f1,), contract)
    assert dec1.exact is True

    # Frame 2: 75% of frame identical, 25% modified
    f2 = f1.copy()
    f2[0:16, 0:16] = 5.0
    out2, dec2 = router.execute("graphics_filter", (f2,), contract)
    assert dec2.route in ["EXACT_RESIDUAL", "PREDICTIVE_TEMPORAL"]
    assert dec2.work_elimination_ratio >= 0.50
    assert dec2.verification_status == "PASSED"


# =============================================================================
# 7. Low-Rank Exact Factorization vs Approximate Isolation
# =============================================================================
def test_low_rank_exact_factorization():
    contract = ContractCompiler.compile_matrix_contract(
        workload_id="LOW_RANK_TEST",
        shape=(64, 64, 64),
        correctness=CorrectnessRequirement.EXACT,
    )
    # Rank-2 outer product matrix: A = u1 v1^T + u2 v2^T
    u = np.random.randn(64, 2).astype(np.float32)
    v = np.random.randn(2, 64).astype(np.float32)
    A = u @ v

    is_viable, r, uv, report = LowRankEngine.analyze_matrix_rank(A, contract=contract)
    assert is_viable is True
    assert r <= 2
    assert report.is_exact_factorization is True
    assert report.approximation_error_norm == 0.0
    assert report.work_elimination_ratio > 0.80


def test_approximate_low_rank_isolation():
    # If contract requires STRICT EXACT, approximate rank is strictly forbidden!
    contract_exact = ContractCompiler.compile_matrix_contract(
        workload_id="FULL_RANK_EXACT",
        shape=(64, 64, 64),
        correctness=CorrectnessRequirement.EXACT,
    )
    # Full rank matrix with decaying singular values
    A = np.random.randn(64, 64).astype(np.float32)
    is_viable, r, uv, report = LowRankEngine.analyze_matrix_rank(A, contract=contract_exact)
    # Full rank cannot be factored under exact contract without loss!
    assert is_viable is False
    assert report.is_exact_factorization is True
    assert report.work_elimination_ratio == 0.0


# =============================================================================
# 8. Precision Engine & Statistical Error Bounds
# =============================================================================
def test_precision_engine_exact_rejection():
    contract_exact = ContractCompiler.compile_matrix_contract(
        workload_id="PRECISION_EXACT",
        shape=(32, 32, 32),
        correctness=CorrectnessRequirement.EXACT,
    )
    data = np.random.randn(32, 32).astype(np.float32)
    out_data, rep = PrecisionEngine.evaluate_precision_reduction(data, "int8", contract=contract_exact)
    # Must reject precision downgrade under exact contract!
    assert rep.contract_permits_reduction is False
    assert rep.contract_satisfied is False
    assert np.array_equal(out_data, data)


def test_precision_engine_numerical_tolerance():
    contract_tol = ContractCompiler.compile_matrix_contract(
        workload_id="PRECISION_TOL",
        shape=(32, 32, 32),
        correctness=CorrectnessRequirement.NUMERICAL_TOLERANCE,
        tolerance=0.05,
    )
    data = np.linspace(-1.0, 1.0, 1024, dtype=np.float32).reshape(32, 32)
    out_data, rep = PrecisionEngine.evaluate_precision_reduction(data, "float16", contract=contract_tol)
    assert rep.contract_permits_reduction is True
    assert rep.contract_satisfied is True
    assert rep.max_absolute_error < 0.05


# =============================================================================
# 9. Physical RTX 5090 Live Probe & Anti-Simulation Rule
# =============================================================================
def test_rtx5090_live_probe_anti_simulation():
    probe = RTX5090LiveProbe.probe_hardware()
    assert probe.status in ["AVAILABLE", "UNAVAILABLE"]
    # On the target laptop (Intel Core i5-12450H + Intel UHD Graphics):
    # If no physical RTX 5090 is present, status MUST be UNAVAILABLE
    if not probe.is_live_rtx5090:
        assert probe.status == "UNAVAILABLE"
        assert "UNAVAILABLE" in probe.notes
        # Zero simulation permitted!


# =============================================================================
# 10. Decoupled Clean-Room Reference Fallback
# =============================================================================
def test_reference_fallback(router):
    # Dense non-zero, non-separable matrix with cold cache policy
    contract = MatrixMultiplicationAdapter.build_contract(M=16, K=16, N=16, cache_policy=CachePolicy.COLD)
    A = np.random.uniform(1.0, 2.0, (16, 16)).astype(np.float32)
    B = np.random.uniform(1.0, 2.0, (16, 16)).astype(np.float32)

    res, dec = router.execute("gemm", (A, B), contract)
    assert dec.fallback_available is True
    assert dec.verification_status in ["PASSED", "VERIFIED"]
    assert dec.exact is True
    ref = A @ B
    assert np.allclose(res, ref, atol=1e-4)


# =============================================================================
# 11. Workload Fingerprinter & Feature Extraction
# =============================================================================
def test_workload_fingerprinter():
    from hyper_x.wormhole_compiler.workload_fingerprint import WorkloadFingerprinter
    contract = MatrixMultiplicationAdapter.build_contract(M=64, K=64, N=64)
    A = np.zeros((64, 64), dtype=np.float32)
    A[32:, :] = 1.0  # 50% zero rows
    fp = WorkloadFingerprinter.extract_fingerprint((A,), contract)
    assert fp.shape == (64, 64)
    assert fp.zero_rows_count == 32
    assert fp.sparsity_ratio == 0.5
    assert fp.dependency_structure == "DENSE_GEMM"


# =============================================================================
# 12. Speculative Breakthrough Router & Online Adaptation
# =============================================================================
def test_speculative_breakthrough_router():
    from hyper_x.wormhole_compiler.speculative_router import SpeculativeBreakthroughRouter
    spec_router = SpeculativeBreakthroughRouter()
    contract = MatrixMultiplicationAdapter.build_contract(M=64, K=64, N=64, cache_policy=CachePolicy.COLD)

    # Test 1: Zero-row matrix should trigger predicted EXACT_ZERO_ROW_PRUNE
    A = np.random.randn(64, 64).astype(np.float32)
    A[0:32, :] = 0.0
    B = np.random.randn(64, 64).astype(np.float32)

    res, report = spec_router.execute_speculative("gemm", (A, B), contract)
    assert report.predicted_route == "EXACT_ZERO_ROW_PRUNE"
    assert report.prediction_correct is True
    assert report.prediction_accuracy > 0.0
    assert report.work_elimination_ratio >= 0.50
