"""
tests/test_five_scoreboards_and_pipeline.py
============================================
Automated tests for:
1. Unified 15-Stage Computational Escape Pipeline (hyper_universal/pipeline.py)
2. Five Independent 100% Scoreboards (hyper_universal/scoreboards.py)
3. Evaluator invariants (isolation, no blended metrics, fallback safety).
"""

import numpy as np
import pytest

from hyper_universal.pipeline import (
    UnifiedComputationalEscapePipeline,
    PipelineContext,
    WorkloadCategory,
)
from hyper_universal.scoreboards import (
    MasterFiveScoreboards,
    ScoreboardStatus,
    Scoreboard1_ExactComputationalParity,
    Scoreboard2_ApplicationContractParity,
    Scoreboard3_PerformanceParity,
    Scoreboard4_MemoryCapacityParity,
    Scoreboard5_DefinedDomainSuccess,
)
from hyper_universal.scoreboards_evaluator import evaluate_live


# =============================================================================
# 1. Pipeline 15-Stage Lifecycle Tests
# =============================================================================
def test_pipeline_exact_execution():
    pipeline = UnifiedComputationalEscapePipeline()
    mat = np.random.randn(64, 64).astype(np.float32)

    # 1st run: Cold run
    ctx = pipeline.execute(
        workload_id="dense_gemm_64",
        input_data=mat,
        execute_fn=lambda a: np.dot(a, a.T),
        reference_oracle_fn=lambda a: np.dot(a, a.T),
    )

    assert ctx.verified is True
    assert ctx.verification_error == 0.0
    assert ctx.fallback_triggered is False
    assert ctx.counterexample_detected is False
    assert ctx.result_label in ("EXACT", "REDUCED_WORK")
    assert ctx.category == WorkloadCategory.EXACT_DETERMINISTIC
    assert "input_validation" in ctx.computation_graph["nodes"]

    # 2nd run: Warm run (exact memoization lookup)
    ctx_warm = pipeline.execute(
        workload_id="dense_gemm_64",
        input_data=mat,
        execute_fn=lambda a: np.dot(a, a.T),
        reference_oracle_fn=lambda a: np.dot(a, a.T),
    )
    assert ctx_warm.result_label == "CACHED"
    assert ctx_warm.verified is True
    assert ctx_warm.elapsed_ms <= ctx.elapsed_ms + 5.0  # Near instantaneous


def test_pipeline_sparse_classification():
    pipeline = UnifiedComputationalEscapePipeline()
    mat = np.random.randn(32, 32).astype(np.float32)

    ctx = pipeline.execute(
        workload_id="sparse_2_4_workload",
        input_data=mat,
    )
    assert ctx.category == WorkloadCategory.SPARSE_STRUCTURED
    assert "2_4_STRUCTURED_SPARSITY_AVX2" in ctx.candidate_transformations


def test_pipeline_counterexample_and_fallback_recovery():
    pipeline = UnifiedComputationalEscapePipeline()
    mat = np.ones((8, 8), dtype=np.float32)

    # Inject deliberate buggy execution to test counterexample detection & fallback
    def buggy_kernel(x):
        return x + 999.0

    def exact_oracle(x):
        return x * 2.0

    ctx = pipeline.execute(
        workload_id="gemm_test_fallback",
        input_data=mat,
        execute_fn=buggy_kernel,
        reference_oracle_fn=exact_oracle,
        exact_reference_fn=exact_oracle,
    )

    # Should detect counterexample and safely recover via exact_reference_fn
    assert ctx.counterexample_detected is True
    assert ctx.fallback_triggered is True
    assert ctx.result_label == "EXACT"
    assert ctx.verified is True
    assert np.allclose(ctx.execution_result, mat * 2.0)


def test_pipeline_fallback_fail_closed_without_oracle():
    pipeline = UnifiedComputationalEscapePipeline()
    mat = np.ones((4, 4), dtype=np.float32)

    def buggy_kernel(x):
        return x + 100.0

    def reference_oracle(x):
        return x * 1.0

    # Without exact_reference_fn, system must fail-closed with EMULATED label and unverified
    ctx = pipeline.execute(
        workload_id="fail_closed_test",
        input_data=mat,
        execute_fn=buggy_kernel,
        reference_oracle_fn=reference_oracle,
        exact_reference_fn=None,
    )

    assert ctx.counterexample_detected is True
    assert ctx.fallback_triggered is True
    assert ctx.verified is False
    assert ctx.result_label == "EMULATED"


# =============================================================================
# 2. Five Independent Scoreboards Isolation Tests
# =============================================================================
def test_scoreboards_strict_isolation():
    """
    INVARIANT: Passing one scoreboard must NEVER automatically mark another as passed.
    Failing or blocking one scoreboard must not affect others.
    """
    sb = MasterFiveScoreboards()

    # 1. Set Scoreboard 1 to PASS
    sb.scoreboard_1.total_exact_workloads = 4
    sb.scoreboard_1.passed_workloads = 4
    sb.scoreboard_1.evaluate()
    assert sb.scoreboard_1.status == ScoreboardStatus.PASS

    # Scoreboards 2-5 remain UNVERIFIED initially
    assert sb.scoreboard_2.status == ScoreboardStatus.UNVERIFIED
    assert sb.scoreboard_3.status == ScoreboardStatus.UNVERIFIED
    assert sb.scoreboard_4.status == ScoreboardStatus.UNVERIFIED
    assert sb.scoreboard_5.status == ScoreboardStatus.UNVERIFIED
    assert sb.all_passed() is False

    # 2. If Scoreboard 3 has missing reference, it must be UNVERIFIED (Rule 8.3)
    sb.scoreboard_3.total_benchmarks = 5
    sb.scoreboard_3.targets_met = 4
    sb.scoreboard_3.reference_unavailable = 1
    sb.scoreboard_3.evaluate()
    assert sb.scoreboard_3.status == ScoreboardStatus.UNVERIFIED

    # Scoreboard 1 must NOT be affected
    assert sb.scoreboard_1.status == ScoreboardStatus.PASS


def test_scoreboards_no_blended_average():
    """
    INVARIANT: No single merged or averaged percentage across scoreboards.
    """
    sb = MasterFiveScoreboards()
    sb.scoreboard_1.total_exact_workloads = 4
    sb.scoreboard_1.passed_workloads = 4
    sb.scoreboard_1.evaluate()

    d = sb.to_dict()
    # Confirm no top-level 'average_percentage' or 'overall_score'
    assert "average_percentage" not in d
    assert "blended_score" not in d
    assert "overall_score" not in d

    # Each scoreboard must have distinct metrics and status
    assert d["scoreboard_1_exact_computational_parity"]["percentage"] == 100.0
    assert d["scoreboard_1_exact_computational_parity"]["status"] == "PASS"


# =============================================================================
# 3. Live Evaluator Verification
# =============================================================================
def test_live_scoreboards_evaluator():
    """
    Verify that evaluate_live() executes real workloads and successfully passes
    all 5 independent scoreboards on the declared supported domain.
    """
    master = evaluate_live()
    assert master.all_passed() is True
    assert master.scoreboard_1.status == ScoreboardStatus.PASS
    assert master.scoreboard_2.status == ScoreboardStatus.PASS
    assert master.scoreboard_3.status == ScoreboardStatus.PASS
    assert master.scoreboard_4.status == ScoreboardStatus.PASS
    assert master.scoreboard_5.status == ScoreboardStatus.PASS
    assert master.scoreboard_3.raw_physical_hardware_parity == 0.0
