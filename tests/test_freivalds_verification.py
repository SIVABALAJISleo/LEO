"""
tests/test_freivalds_verification.py
====================================
Tests Phase 12 Freivalds probabilistic matrix multiplication verification.
Verifies O(k N^2) stochastic checking and undetected error probability reporting.
"""

import numpy as np
import pytest
from hyper.verification.verifier import VerificationEngine


def test_freivalds_passes_on_correct_product():
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)
    C = A @ B

    report = VerificationEngine.verify_freivalds(A, B, C, num_trials=5)
    assert report["is_probabilistically_consistent"] is True
    assert report["number_of_trials"] == 5
    assert report["estimated_undetected_error_probability"] == 2.0 ** (-5)
    assert "caveat" in report


def test_freivalds_detects_corrupted_product():
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)
    C = A @ B

    # Corrupt single element
    C_corrupt = C.copy()
    C_corrupt[10, 10] += 5.0

    report = VerificationEngine.verify_freivalds(A, B, C_corrupt, num_trials=5)
    assert report["is_probabilistically_consistent"] is False
    assert report["max_relative_residual"] > 1e-3
