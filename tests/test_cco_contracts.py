"""
tests/test_cco_contracts.py
===========================
Unit tests for ComputeContract and 12-Class Correctness Taxonomy.
"""

import pytest
import numpy as np
from hyper_cco.contract import (
    ComputeContract,
    ExactnessClass,
    VerificationLevel,
    VerificationStatus,
    ContractViolationError
)


def test_contract_creation_and_hash():
    c1 = ComputeContract(
        workload_id="GEMM_TEST",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_relative_error=1e-3,
        max_latency_ms=25.0
    )
    c2 = ComputeContract(
        workload_id="GEMM_TEST",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_relative_error=1e-3,
        max_latency_ms=25.0
    )
    c3 = ComputeContract(
        workload_id="GEMM_TEST",
        exactness_class=ExactnessClass.EXACT,
        max_relative_error=0.0
    )
    assert c1.compute_hash() == c2.compute_hash()
    assert c1.compute_hash() != c3.compute_hash()


def test_contract_validation_exact_pass():
    contract = ComputeContract(
        workload_id="EXACT_TEST",
        exactness_class=ExactnessClass.EXACT
    )
    base = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    cand = base.copy()
    valid, status, metrics = contract.validate_metrics(cand, base)
    assert valid is True
    assert status == VerificationStatus.PASS
    assert metrics["error_abs"] == 0.0


def test_contract_validation_exact_fail_on_noise():
    contract = ComputeContract(
        workload_id="EXACT_TEST",
        exactness_class=ExactnessClass.EXACT
    )
    base = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    cand = base + 1e-6
    valid, status, metrics = contract.validate_metrics(cand, base)
    assert valid is False
    assert status == VerificationStatus.FAIL
    assert "Exactness required" in metrics["violation_reason"]


def test_contract_validation_numerical_tolerance():
    contract = ComputeContract(
        workload_id="NUM_TOL_TEST",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=None,
        max_relative_error=1e-3
    )
    base = np.ones((10, 10), dtype=np.float32)
    cand_good = base + 1e-4
    valid, status, _ = contract.validate_metrics(cand_good, base)
    assert valid is True
    assert status == VerificationStatus.PASS

    cand_bad = base + 1e-2
    valid_bad, status_bad, metrics_bad = contract.validate_metrics(cand_bad, base)
    assert valid_bad is False
    assert status_bad == VerificationStatus.FAIL
    assert "Max relative error" in metrics_bad["violation_reason"]


def test_contract_shape_dtype_invariance():
    contract = ComputeContract(
        workload_id="SHAPE_TEST",
        output_shape=(4, 4),
        output_dtype="float32"
    )
    cand_wrong_shape = np.ones((4, 5), dtype=np.float32)
    valid, status, metrics = contract.validate_metrics(cand_wrong_shape)
    assert valid is False
    assert "Shape mismatch" in metrics["violation_reason"]

    cand_wrong_dtype = np.ones((4, 4), dtype=np.float64)
    valid2, status2, metrics2 = contract.validate_metrics(cand_wrong_dtype)
    assert valid2 is False
    assert "Dtype mismatch" in metrics2["violation_reason"]
