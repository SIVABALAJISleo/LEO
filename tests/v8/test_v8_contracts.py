"""
tests/v8/test_v8_contracts.py
=============================
Tests for ComputeContractV2, ContractValidator, and PathClassification.
"""

import numpy as np
import pytest

from hyper.v8.contract import (
    ComputeContractV2,
    ContractValidator,
    PathClassification,
    VerificationStatus,
    exact_contract,
    numerical_contract,
    realtime_contract,
)


def test_exact_contract_pass():
    contract = exact_contract("test_exact")
    validator = ContractValidator()

    ref = np.array([[1.0, 2.0], [3.0, 4.0]])
    cand = ref.copy()

    result = validator.validate(contract, ref, cand, PathClassification.EXACT_FRESH, 1.0)
    assert result.passed
    assert result.verification_status == VerificationStatus.VERIFIED_EXACT
    assert result.max_abs_error == 0.0


def test_exact_contract_fail():
    contract = exact_contract("test_exact_fail")
    validator = ContractValidator()

    ref = np.array([[1.0, 2.0], [3.0, 4.0]])
    cand = ref + 0.01  # Exceeds 0.0

    result = validator.validate(contract, ref, cand, PathClassification.EXACT_FRESH, 1.0)
    assert not result.passed
    assert result.verification_status == VerificationStatus.REJECTED


def test_numerical_contract_pass():
    contract = numerical_contract("test_approx", abs_tol=1e-2, rel_tol=1e-2)
    validator = ContractValidator()

    ref = np.array([[100.0, 200.0], [300.0, 400.0]])
    cand = ref + 0.005  # Within 1e-2 tolerance

    result = validator.validate(contract, ref, cand, PathClassification.APPROXIMATE, 1.0)
    assert result.passed
    assert result.verification_status == VerificationStatus.VERIFIED_NUMERICAL


def test_realtime_contract_deadline():
    contract = realtime_contract(fps=60.0, abs_tol=1e-3)
    validator = ContractValidator()

    ref = np.ones((5, 5))
    cand = ref.copy()

    # Latency within deadline (1000/60 = 16.6ms)
    res1 = validator.validate(contract, ref, cand, PathClassification.EXACT_FRESH, 3.0)
    assert res1.passed

    # Latency exceeds deadline
    res2 = validator.validate(contract, ref, cand, PathClassification.EXACT_FRESH, 25.0)
    assert not res2.passed
    assert res2.verification_status == VerificationStatus.REJECTED
