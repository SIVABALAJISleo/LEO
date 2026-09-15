"""
tests/test_low_rank_break_even.py
=================================
Tests Phase 8 low-rank factorization, break-even reuse analysis,
and adversarial high-rank matrix fallback.
"""

import numpy as np
import pytest
from hyper.low_rank.low_rank_engine import LowRankEngine


def test_low_rank_break_even_calculation():
    engine = LowRankEngine(default_rank=8)
    rng = np.random.RandomState(42)

    # Intrinsically low-rank matrix
    U = rng.randn(128, 8).astype(np.float32)
    V = rng.randn(8, 128).astype(np.float32)
    A = U @ V
    B = rng.randn(128, 128).astype(np.float32)

    # 1. One-shot execution (reuse = 1) -> factorization cost makes it more expensive or break-even > 1
    _, report_1shot = engine.benchmark_and_execute(A, B, rank=8, expected_reuse_count=1)
    assert "break_even_reuse_count" in report_1shot
    assert report_1shot["break_even_reuse_count"] >= 1

    # 2. High reuse count (e.g. 1000) -> Low rank is beneficial
    _, report_multi = engine.benchmark_and_execute(A, B, rank=8, expected_reuse_count=10000)
    assert report_multi["is_beneficial"] is True
    assert report_multi["path_class"] == "NUMERICALLY_APPROXIMATE"


def test_hostile_full_rank_matrix_rejection():
    engine = LowRankEngine(default_rank=4)
    rng = np.random.RandomState(42)

    # Hostile: pure random full-rank noise with uniform singular values
    A = rng.randn(64, 64).astype(np.float32)
    B = rng.randn(64, 64).astype(np.float32)

    # Strict contract: max relative error 0.01
    _, report = engine.benchmark_and_execute(
        A, B, rank=4, expected_reuse_count=100, max_allowed_rel_error=0.01
    )
    # Rank 4 cannot represent full-rank 64x64 matrix within 1% error
    assert report["error_acceptable"] is False
    assert report["path_class"] == "EXACT"
