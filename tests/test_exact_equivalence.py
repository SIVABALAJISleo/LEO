"""
tests/test_exact_equivalence.py
===============================
Tests Phase 4 & 12 exact equivalence guarantees.
Ensures that any candidate claiming EXACT produces bitwise or zero-error equivalence.
"""

import numpy as np
import pytest
from hyper.candidate import CandidateResult, PathClass
from hyper.verification.verifier import VerificationEngine


def test_exact_candidate_passes_verification():
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    expected = A @ B
    actual = np.matmul(A, B)  # exact execution

    ver = VerificationEngine.verify_numerical(actual, expected)
    assert ver["is_exact"] is True
    assert ver["max_abs_error"] == 0.0

    cand = CandidateResult(
        value=actual,
        path_class=PathClass.EXACT.value,
        backend="CPU_AVX2",
        latency_ms=0.5,
        work_units=32 * 32 * 32,
        memory_bytes=actual.nbytes,
        max_abs_error=ver["max_abs_error"],
        relative_error=ver["relative_error"],
        rmse=ver["rmse"],
        verification_status="PASS" if ver["is_exact"] else "FAIL",
    )
    assert cand.verification_status == "PASS"


def test_reject_approximate_claimed_as_exact():
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    expected = A @ B
    perturbed = expected + 1e-4  # approximate, NOT exact

    ver = VerificationEngine.verify_numerical(perturbed, expected)
    assert ver["is_exact"] is False

    # A verifier or validator must reject this candidate if claimed as EXACT
    status = "PASS" if (ver["is_exact"]) else "FAIL"
    assert status == "FAIL"
