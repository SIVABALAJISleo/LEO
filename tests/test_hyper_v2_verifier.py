"""
tests/test_hyper_v2_verifier.py
Unit tests for Independent Verifier, Freivalds, SSIM, and Fallback Ladder.
"""

import pytest
import numpy as np
from hyper_v2.verification.independent_verifier import IndependentVerifier
from hyper_v2.strategies.fallback_ladder import FallbackLadderExecutor, FallbackLevel


def test_freivalds_verifier():
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    C_exact = np.matmul(A, B)

    # Valid matrix product
    res_pass = IndependentVerifier.verify_freivalds_matmul(A, B, C_exact, epsilon=1e-3)
    assert res_pass.is_verified is True

    # Corrupted matrix product
    C_corrupt = C_exact + 5.0
    res_fail = IndependentVerifier.verify_freivalds_matmul(A, B, C_corrupt, epsilon=1e-3)
    assert res_fail.is_verified is False


def test_ssim_verifier():
    img1 = np.ones((64, 64), dtype=np.float32) * 128.0
    img2 = img1.copy()
    res = IndependentVerifier.verify_ssim(img1, img2, min_ssim=0.95)
    assert res.is_verified is True
    assert res.measured_value >= 0.999


def test_fallback_ladder_execution():
    # Setup ladder with a failing level 0 and a passing level 2
    ladder_fns = {
        FallbackLevel.LEVEL_0_REUSE: lambda: "corrupt_data",
        FallbackLevel.LEVEL_2_EXACT_REFORMULATION: lambda: "verified_good_data",
        FallbackLevel.LEVEL_8_EXACT_FALLBACK: lambda: "exact_fallback_data"
    }

    def verify(data):
        return "good" in data

    outcome = FallbackLadderExecutor.execute_with_fallback(
        target_name="test_target",
        ladder_fns=ladder_fns,
        verifier_fn=verify
    )
    assert outcome["verified"] is True
    assert outcome["final_level"] == int(FallbackLevel.LEVEL_2_EXACT_REFORMULATION)
