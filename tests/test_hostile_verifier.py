"""
tests/test_hostile_verifier.py
==============================
Hostile Self-Falsification Suite: Verifier & Anti-Truncation Invariants.

Verifies that the verifier cannot be fooled by:
  - Shorter candidate outputs (anti-truncation rule: candidates shorter than baseline MUST FAIL)
  - Single perturbed elements
  - NaN or Inf injection
  - Zero-norm trivial bypasses
  - Dimension / shape mismatch
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass, EvidenceClass, VerificationStatus


def test_anti_truncation_enforcement():
    """Candidates shorter than baseline must immediately fail."""
    contract = ComputeContract(
        workload_id="HOSTILE_TRUNC",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-3,
        output_shape=(100,),
    )
    baseline = np.ones(100, dtype=np.float32)
    candidate_short = np.ones(90, dtype=np.float32)

    passed, status, metrics = contract.validate(candidate_short, baseline)
    assert passed is False
    assert status == VerificationStatus.FAIL
    assert "Shape mismatch" in metrics["violation_reason"] or "Short candidate" in metrics["violation_reason"]


def test_single_element_corruption():
    """A single corrupted element beyond tolerance must fail verification."""
    contract = ComputeContract(
        workload_id="HOSTILE_CORRUPT",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-4,
        output_shape=(50, 50),
    )
    baseline = np.ones((50, 50), dtype=np.float32)
    candidate = baseline.copy()
    candidate[25, 25] += 0.05  # Corrupt single element

    passed, status, metrics = contract.validate(candidate, baseline)
    assert passed is False
    assert status == VerificationStatus.FAIL
    assert metrics["error_abs"] >= 0.049


def test_nan_injection_rejection():
    """Injected NaN values must immediately fail verification without crashing."""
    contract = ComputeContract(
        workload_id="HOSTILE_NAN",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-3,
        output_shape=(20,),
    )
    baseline = np.ones(20, dtype=np.float32)
    candidate = baseline.copy()
    candidate[5] = np.nan

    passed, status, metrics = contract.validate(candidate, baseline)
    assert passed is False
    assert status == VerificationStatus.FAIL
    assert "non-finite" in metrics["violation_reason"].lower() or "nan" in metrics["violation_reason"].lower()


def test_inf_injection_rejection():
    """Injected Inf values must immediately fail verification."""
    contract = ComputeContract(
        workload_id="HOSTILE_INF",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-3,
        output_shape=(20,),
    )
    baseline = np.ones(20, dtype=np.float32)
    candidate = baseline.copy()
    candidate[10] = np.inf

    passed, status, metrics = contract.validate(candidate, baseline)
    assert passed is False
    assert status == VerificationStatus.FAIL
    assert "non-finite" in metrics["violation_reason"].lower() or "inf" in metrics["violation_reason"].lower()


def test_zero_candidate_rejection():
    """All-zero candidate against non-zero baseline must fail verification."""
    contract = ComputeContract(
        workload_id="HOSTILE_ZERO",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_relative_error=1e-3,
        output_shape=(30,),
    )
    baseline = np.ones(30, dtype=np.float32) * 5.0
    candidate = np.zeros(30, dtype=np.float32)

    passed, status, metrics = contract.validate(candidate, baseline)
    assert passed is False
    assert status == VerificationStatus.FAIL
    assert metrics["error_rel"] >= 0.99
