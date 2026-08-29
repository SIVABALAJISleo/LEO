"""
tests/test_hyper100_falsification.py
====================================
Hostile Self-Falsification Suite for HYPER-100.
Specifically tests adversarial edge cases, high-entropy inputs, zero-error contracts,
cache isolation, numerical singularities, Winograd/Woodbury/Welford correctness, and fallback guarantees.
"""

import pytest
import numpy as np

from hyper100.contract_engine import ExecutionContract, ContractExactness, VerificationStatus, ContractViolationError
from hyper100.workload_analyzer import WorkloadAnalyzer
from hyper100.redundancy_discovery import RedundancyDiscoveryEngine
from hyper100.elimination_engine import ComputationEliminationEngine
from hyper100.cache_reuse_engine import CacheReuseEngine, CacheMode
from hyper100.sparsity_engine import SparsityEngine
from hyper100.low_rank_engine import LowRankEngine
from hyper100.precision_engine import PrecisionEngine, PrecisionFormat
from hyper100.prediction_engine import PredictionEngine
from hyper100.algorithmic_reformulation import AlgorithmicReformulationEngine
from hyper100.information_reduction import InformationReductionEngine
from hyper100.verification_engine import VerificationEngine
from hyper100.adaptive_fallback import AdaptiveFallbackEngine
from hyper100.runtime import Hyper100Runtime
from hyper100.universal_orchestrator import UniversalOrchestrator


class TestHostileFalsification:

    def test_1_high_entropy_incompressible_matrix_not_falsified(self):
        """Adversarial Test: Random high-entropy Gaussian matrix must NOT report false redundancy."""
        np.random.seed(42)
        dense_noise = np.random.randn(256, 256).astype(np.float32)
        report = RedundancyDiscoveryEngine.analyze_tensor(dense_noise)

        # Full-rank random noise should have high rank (>= 190) and zero redundancy score
        assert report.sparsity_ratio < 0.05
        assert report.rank_estimate >= 190
        assert report.redundancy_score == 0.0
        assert "DENSE_EXACT_BASELINE" in report.recommended_transformations

    def test_2_exact_contract_strictly_forbids_approximation(self):
        """Contract Test: EXACT contract must reject low-rank/quantization and produce 0.0 error."""
        runtime = Hyper100Runtime()
        contract = ExecutionContract(exactness=ContractExactness.EXACT)

        A = np.random.randn(128, 128).astype(np.float32)
        B = np.random.randn(128, 64).astype(np.float32)

        out, record = runtime.execute_matmul(A, B, contract)
        baseline = A @ B

        assert np.array_equal(out, baseline) or np.max(np.abs(out - baseline)) == 0.0
        assert record.verification_status == "EXACT"
        assert record.measured_absolute_error == 0.0

    def test_3_ill_conditioned_matrix_svd_stability(self):
        """Numerical Test: Ill-conditioned matrix with extreme condition number does not crash."""
        # Create matrix with singular values decaying from 1e6 down to 1e-12
        U, _ = np.linalg.qr(np.random.randn(64, 64))
        V, _ = np.linalg.qr(np.random.randn(64, 64))
        S = np.logspace(6, -12, 64)
        ill_mat = (U @ np.diag(S) @ V).astype(np.float32)

        decomp, rep = LowRankEngine.factorize_matrix(ill_mat, target_rank=16)
        assert decomp.rank == 16
        assert not np.isnan(decomp.U).any()
        assert not np.isnan(decomp.Vh).any()

    def test_4_cache_mode_isolation(self):
        """Cache Isolation Test: Cold vs Disabled modes prevent cache contamination."""
        cache = CacheReuseEngine(default_mode=CacheMode.CACHE_DISABLED)
        A = np.ones((10, 10), dtype=np.float32)
        key = cache.compute_tensor_key("test_op", A)

        cache.insert(key, A)
        res = cache.lookup(key)
        assert res.hit is False  # Cache disabled mode must always return miss

        cache.set_mode(CacheMode.WARM)
        cache.insert(key, A)
        res_warm = cache.lookup(key)
        assert res_warm.hit is True

        cache.set_mode(CacheMode.COLD)
        res_cold = cache.lookup(key)
        assert res_cold.hit is False  # Cold mode clears and isolates

    def test_5_forced_candidate_failure_triggers_exact_fallback(self):
        """Fallback Test: A failing candidate optimization must automatically trigger exact fallback."""
        contract = ExecutionContract(exactness=ContractExactness.EXACT)

        def failing_candidate():
            return np.ones((5, 5)) * 999.0  # Intentional error

        def exact_baseline():
            return np.ones((5, 5)) * 42.0

        candidates = [("FAILING_CANDIDATE", failing_candidate)]
        result, trace = AdaptiveFallbackEngine.execute_with_fallback(
            candidates,
            exact_baseline,
            contract
        )

        assert trace.fallback_triggered is True
        assert trace.final_strategy == "EXACT_BASELINE_FALLBACK"
        assert np.array_equal(result, np.ones((5, 5)) * 42.0)

    def test_6_prediction_residual_rejection_on_sudden_state_jump(self):
        """Prediction Test: A sudden discontinuity in temporal state causes prediction to be rejected."""
        contract = ExecutionContract(max_error=0.01)
        S_prev = np.zeros((32, 32), dtype=np.float32)
        S_curr = np.ones((32, 32), dtype=np.float32) * 50.0  # Sudden massive shockwave

        pred, report = PredictionEngine.predict_temporal_state([S_prev, S_curr], contract)
        # Drift is large (50.0 > 0.01), so prediction must be rejected
        assert report.prediction_accepted is False

    def test_7_precision_quantization_bounded_error_contract(self):
        """Precision Test: Quantization format is rejected if it violates contract max_error."""
        strict_contract = ExecutionContract(exactness=ContractExactness.BOUNDED_ERROR, max_error=1e-5)
        tensor = np.random.randn(64, 64).astype(np.float32)

        out, fmt, rep = PrecisionEngine.optimize_precision(tensor, strict_contract)
        # INT8 error is ~1e-2 which violates 1e-5, so FP32 must be chosen
        assert fmt == PrecisionFormat.FP32
        assert rep.satisfies_contract is True

    def test_8_winograd_minimal_filtering_exact_equivalence(self):
        """Algorithmic Test: Winograd F(2x2, 3x3) minimal filter output matches direct convolution."""
        tile = np.random.randn(4, 4).astype(np.float32)
        kernel = np.array([[0.1, -0.5, 0.2], [-0.3, 1.2, -0.4], [0.5, -0.1, 0.8]], dtype=np.float32)

        out_winograd, rep = AlgorithmicReformulationEngine.winograd_conv2d_3x3(tile, kernel)
        assert rep.is_exact_equivalent is True
        assert rep.max_numerical_difference < 1e-4

    def test_9_woodbury_rank_k_inverse_stability(self):
        """Algorithmic Test: Woodbury rank-k inverse update matches direct matrix inversion."""
        N = 64
        k = 4
        A = np.eye(N, dtype=np.float32) + 0.05 * np.random.randn(N, N).astype(np.float32)
        A_inv = np.linalg.inv(A)
        U = np.random.randn(N, k).astype(np.float32)
        V = np.random.randn(k, N).astype(np.float32)
        C = np.eye(k, dtype=np.float32)

        updated_inv, rep = AlgorithmicReformulationEngine.woodbury_rank_k_inverse_update(A_inv, U, C, V)
        direct_inv = np.linalg.inv(A + U @ C @ V)
        max_diff = float(np.max(np.abs(updated_inv - direct_inv)))
        assert max_diff < 1e-3

    def test_10_welford_online_statistics_numerical_stability(self):
        """Algorithmic Test: Welford single-pass variance on ill-conditioned shifted numbers."""
        # Ill-conditioned dataset: mean = 1e9, variance = 1.0
        data = np.array([1e9 + 1.0, 1e9 + 2.0, 1e9 + 3.0, 1e9 + 4.0, 1e9 + 5.0], dtype=np.float64)
        mean, var, rep = AlgorithmicReformulationEngine.welford_online_statistics(data)

        expected_var = float(np.var(data, ddof=1))
        assert abs(var - expected_var) < 1e-4
