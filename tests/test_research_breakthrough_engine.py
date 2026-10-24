"""
tests/test_research_breakthrough_engine.py
==========================================
Comprehensive Automated Test Battery for the LEO/HYPER Research Breakthrough Engine.

Verifies:
1. Automated Algorithm Discovery Subsystem (Bounded Search, Candidate Generation, Cost Guard).
2. Research Memory & Failed-Attempt Learning Database (Categorization, Querying, Recommendation).
3. Real Application Workloads Suite (MHA Attention, MLP, Sobel Filter, Wave Stencil, HDR Tone Mapping).
4. Memory-Aware Computation & Streamed Freivalds Verification.
"""

import math
import os
import tempfile
import time
import numpy as np
import pytest

import hyper_phase_change as hpc
from hyper_phase_change.discovery import (
    CandidateStatus,
    DiscoveryBudget,
    CandidateProfile,
    DiscoverySearchResult,
    AlgorithmDiscoveryEngine,
)
from hyper_phase_change.experiment_db import (
    FailureCategory,
    ExperimentRecord,
    ResearchExperimentDB,
    EXPERIMENT_DB,
)
from hyper_phase_change.real_workloads import RealWorkloadSuite
from backend.hardware.universal_subsumption_engine import (
    ZeroRejectionEngine,
    UniversalSubsumptionEngine,
)


class TestAlgorithmDiscoveryEngine:
    """Verifies bounded search, candidate generation, and discovery cost guards."""

    def test_discovery_cost_guard_bypasses_tiny_workload(self):
        """Verifies that discovery search is bypassed for tiny inputs to avoid optimization overhead."""
        inputs = {
            "A": np.eye(8, dtype=np.float32),
            "B": np.ones((8, 8), dtype=np.float32),
        }
        res = AlgorithmDiscoveryEngine.run_discovery_search("GEMM_STANDARD", inputs)
        assert res.search_bypassed_by_guard is True
        assert res.achieved_speedup >= 1.0
        assert res.best_candidate is not None
        assert res.best_candidate.is_correct is True
        assert "Cost Guard" in res.best_candidate.description

    def test_discovery_bounded_search_on_structured_gemm(self):
        """Verifies candidate generation and discovery of spectral residual boosting on structured GEMM."""
        rng = np.random.RandomState(42)
        # Create rank-8 structured matrix of size 128x128 (> 4096 elements to pass cost guard)
        U = rng.randn(128, 8).astype(np.float32)
        V = rng.randn(8, 128).astype(np.float32)
        A = U @ V
        B = rng.randn(128, 128).astype(np.float32)

        inputs = {"A": A, "B": B}
        budget = DiscoveryBudget(time_budget_ms=1000.0, max_candidates=5)

        res = AlgorithmDiscoveryEngine.run_discovery_search("GEMM_STANDARD", inputs, budget=budget)
        assert res.search_bypassed_by_guard is False
        assert res.candidates_evaluated >= 2
        assert res.best_candidate is not None
        assert res.best_candidate.is_correct is True
        assert res.best_candidate.status == CandidateStatus.ACCEPTED
        assert res.best_latency_ms > 0.0

    def test_discovery_budget_strict_timeout_enforcement(self):
        """Verifies that the search strictly respects the time budget and does not hang."""
        inputs = {
            "A": np.random.randn(256, 256).astype(np.float32),
            "B": np.random.randn(256, 256).astype(np.float32),
        }
        # Enforce strict 10ms budget
        budget = DiscoveryBudget(time_budget_ms=10.0, max_candidates=10)
        t0 = time.perf_counter()
        res = AlgorithmDiscoveryEngine.run_discovery_search("GEMM_STANDARD", inputs, budget=budget)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Must return promptly without exceeding budget significantly
        assert elapsed_ms < 500.0
        assert res.best_candidate is not None

    def test_discovery_cancellation_token(self):
        """Verifies cancellation support halts candidate generation immediately."""
        inputs = {
            "A": np.random.randn(128, 128).astype(np.float32),
            "B": np.random.randn(128, 128).astype(np.float32),
        }
        budget = DiscoveryBudget(cancellation_requested=True)
        res = AlgorithmDiscoveryEngine.run_discovery_search("GEMM_STANDARD", inputs, budget=budget)
        # Should evaluate at most the baseline candidate
        assert res.candidates_evaluated <= 1


class TestResearchExperimentDB:
    """Verifies failed-attempt learning and empirical research memory."""

    def test_experiment_db_persistence_and_querying(self):
        """Verifies recording, categorization, and querying of empirical experiments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_exp_db.jsonl")
            db = ResearchExperimentDB(db_path=db_path)

            # Record failure
            db.record_experiment(
                experiment_id="EXP-TEST-001",
                workload_id="GEMM_TEST",
                hypothesis="Aggressive low-rank truncation works on white noise",
                baseline_backend="CPU_AVX2",
                baseline_latency_ms=2.5,
                candidate_id="cand_bad_trunc",
                candidate_transformation="LOW_RANK",
                input_domain={"shape": [128, 128]},
                correctness_evidence=False,
                max_observed_error=0.45,
                performance_evidence=False,
                candidate_latency_ms=5.0,
                speedup=0.5,
                result="REJECTED",
                failure_category=FailureCategory.NUMERICAL_INSTABILITY,
                failure_details="Frobenius error exceeded contract atol",
                next_experiment="Use exact BLAS fallback",
            )

            # Record success
            db.record_experiment(
                experiment_id="EXP-TEST-002",
                workload_id="GEMM_TEST",
                hypothesis="Spectral boosting satisfies contract",
                baseline_backend="CPU_AVX2",
                baseline_latency_ms=2.5,
                candidate_id="cand_spectral",
                candidate_transformation="SPECTRAL_BOOST",
                input_domain={"shape": [128, 128]},
                correctness_evidence=True,
                max_observed_error=0.0001,
                performance_evidence=True,
                candidate_latency_ms=0.8,
                speedup=3.12,
                result="ACCEPTED",
                failure_category=FailureCategory.NONE,
                next_experiment="Proceed",
            )

            # Query failures
            failures = db.query_failures(FailureCategory.NUMERICAL_INSTABILITY)
            assert len(failures) == 1
            assert failures[0].experiment_id == "EXP-TEST-001"
            assert failures[0].max_observed_error == 0.45

            # Strategy recommendation
            rec = db.recommend_next_strategy("GEMM_TEST")
            assert "numerical instability" in rec.lower()

            # Markdown summary
            md = db.generate_markdown_summary()
            assert "Total Experiments Recorded" in md
            assert "2" in md
            assert "NUMERICAL_INSTABILITY" in md


class TestRealApplicationWorkloads:
    """Verifies the expanded real application workloads beyond synthetic benchmarks."""

    def test_mha_multi_head_attention_numerical_equivalence(self):
        """Verifies Multi-Head Attention inference candidate against independent analytical reference."""
        rng = np.random.RandomState(42)
        Q = rng.randn(64, 64).astype(np.float32)
        K = rng.randn(64, 64).astype(np.float32)
        V = rng.randn(64, 64).astype(np.float32)

        inputs = {"Q": Q, "K": K, "V": V}
        ref_out = RealWorkloadSuite.ref_mha_attention(inputs)
        cand_out = RealWorkloadSuite.cand_mha_attention(inputs)

        assert ref_out.shape == (64, 64)
        assert np.allclose(ref_out, cand_out, atol=1e-4, rtol=1e-4)

        # Independent verification check
        v_res = hpc.PhaseChangeVerifier.verify_candidate_output(
            "ML_MHA_ATTENTION", inputs, cand_out, reference_output=ref_out
        )
        assert v_res.is_verified is True
        assert v_res.status == hpc.VerificationStatus.PASS

    def test_mlp_neural_inference_numerical_equivalence(self):
        """Verifies 2-layer MLP neural inference candidate against independent reference."""
        rng = np.random.RandomState(42)
        inputs = {
            "X": rng.randn(32, 64).astype(np.float32),
            "W1": rng.randn(64, 128).astype(np.float32) * 0.1,
            "b1": np.zeros(128, dtype=np.float32),
            "W2": rng.randn(128, 10).astype(np.float32) * 0.1,
            "b2": np.zeros(10, dtype=np.float32),
        }
        ref_out = RealWorkloadSuite.ref_mlp_inference(inputs)
        cand_out = RealWorkloadSuite.cand_mlp_inference(inputs)

        assert ref_out.shape == (32, 10)
        assert np.allclose(ref_out, cand_out, atol=1e-4, rtol=1e-4)

        v_res = hpc.PhaseChangeVerifier.verify_candidate_output(
            "ML_MLP_INFERENCE", inputs, cand_out, reference_output=ref_out
        )
        assert v_res.is_verified is True

    def test_vision_sobel_gaussian_filter_numerical_equivalence(self):
        """Verifies 2D Sobel edge filter candidate against independent nested loop reference."""
        rng = np.random.RandomState(42)
        img = rng.uniform(0.0, 1.0, size=(64, 64)).astype(np.float32)
        inputs = {"img": img}

        ref_out = RealWorkloadSuite.ref_vision_filter(inputs)
        cand_out = RealWorkloadSuite.cand_vision_filter(inputs)

        assert ref_out.shape == (64, 64)
        assert np.allclose(ref_out, cand_out, atol=1e-4, rtol=1e-4)

    def test_simulation_wave_equation_numerical_equivalence(self):
        """Verifies 2D FDTD wave propagation stencil candidate against independent reference."""
        grid = np.zeros((64, 64), dtype=np.float32)
        grid[32, 32] = 1.0  # impulse in center
        inputs = {
            "u": grid,
            "u_prev": np.zeros((64, 64), dtype=np.float32),
            "courant_sq": 0.25,
        }

        ref_out = RealWorkloadSuite.ref_wave_simulation(inputs)
        cand_out = RealWorkloadSuite.cand_wave_simulation(inputs)

        assert ref_out.shape == (64, 64)
        assert np.allclose(ref_out, cand_out, atol=1e-4, rtol=1e-4)

    def test_graphics_hdr_tonemapping_numerical_equivalence(self):
        """Verifies HDR Reinhard tone mapping candidate against independent reference."""
        rng = np.random.RandomState(42)
        hdr_rgb = rng.uniform(0.0, 10.0, size=(32, 32, 3)).astype(np.float32)
        inputs = {"hdr_rgb": hdr_rgb}

        ref_out = RealWorkloadSuite.ref_graphics_tone_map(inputs)
        cand_out = RealWorkloadSuite.cand_graphics_tone_map(inputs)

        assert ref_out.shape == (32, 32, 3)
        assert np.all(cand_out >= 0.0)
        assert np.all(cand_out <= 1.0)
        assert np.allclose(ref_out, cand_out, atol=1e-4, rtol=1e-4)


class TestMemoryAndSubsumptionPillars:
    """Verifies memory bounds and out-of-core streaming."""

    def test_streamed_freivalds_probabilistic_verification(self):
        """Verifies that streamed Freivalds verification detects correct vs corrupted matrices in O(k N^2)."""
        rng = np.random.RandomState(42)
        A = rng.randn(100, 100).astype(np.float32)
        B = rng.randn(100, 100).astype(np.float32)
        C_correct = A @ B

        # Correct matrix must pass
        is_valid, err = ZeroRejectionEngine.verify_freivalds_streamed(A, B, C_correct, k=5, epsilon=1e-3)
        assert is_valid is True
        assert err <= 1e-3

        # Corrupt single element
        C_corrupted = C_correct.copy()
        C_corrupted[50, 50] += 5.0
        is_valid_bad, err_bad = ZeroRejectionEngine.verify_freivalds_streamed(A, B, C_corrupted, k=5, epsilon=1e-3)
        assert is_valid_bad is False
        assert err_bad > 1e-3
