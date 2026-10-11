"""
tests/hyper_escape/test_contracts.py
Validates Universal Workload Contract Engine (Feature A).
Tests contract registration, exactness modes, numerical tolerance enforcement,
resource constraints, and fail-closed differential verification.
"""
import pytest
import numpy as np

from hyper_universal.contracts.contract_engine import (
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
    ContractRegistry,
    differential_contract_verify,
)


def test_contract_registry_default_contracts():
    registry = ContractRegistry()
    contracts = registry.list_contracts()
    assert len(contracts) >= 4

    gemm_contract = registry.get("dense_gemm_512x512")
    assert gemm_contract is not None
    assert gemm_contract.exactness_requirement == ExactnessRequirement.NUMERICALLY_EQUIVALENT
    assert gemm_contract.tolerance.max_relative_error == 1e-4

    fft_contract = registry.get("fft_spectral_1024")
    assert fft_contract is not None
    assert fft_contract.exactness_requirement == ExactnessRequirement.NUMERICALLY_EQUIVALENT


def test_contract_bitwise_exact_verification():
    contract = UniversalContract(
        workload_id="crypto_sha256",
        category="cryptography",
        description="Exact bitwise hash check",
        input_schema={"dtype": "uint8"},
        output_schema={"dtype": "uint8"},
        exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
        tolerance=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
    cand_match = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
    cand_mismatch = np.array([1, 2, 3, 4, 6], dtype=np.uint8)

    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand_match, ref)
    assert passed is True
    assert max_abs == 0.0

    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand_mismatch, ref)
    assert passed is False
    assert "Bitwise mismatch" in reason


def test_contract_conjunctive_tolerance_enforcement():
    # Contract requires BOTH max_rel <= 0.01 AND max_abs <= 0.1
    contract = UniversalContract(
        workload_id="sensor_filter",
        category="signal_processing",
        description="Filter with strict conjunctive bounds",
        input_schema={"shape": [100]},
        output_schema={"shape": [100]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=0.01, max_absolute_error=0.1),
        resource_budget=ResourceBudget(max_memory_mb=128.0),
    )

    ref = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    # Cand 1: max_rel = 0.005 (ok), max_abs = 0.05 (ok) -> Pass
    cand1 = np.array([10.05, 20.05, 30.05], dtype=np.float32)
    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand1, ref)
    assert passed is True

    # Cand 2: large absolute error on a large value -> relative error is small (0.008), but absolute is 0.8 (> 0.1) -> FAIL
    ref_large = np.array([100.0, 200.0], dtype=np.float32)
    cand_violates_abs = np.array([100.8, 200.0], dtype=np.float32)
    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand_violates_abs, ref_large)
    assert passed is False
    assert "exceeds contract tolerance" in reason


def test_contract_nan_inf_rejection():
    contract = UniversalContract(
        workload_id="sim_physics",
        category="simulation",
        description="Simulation rejecting non-finite values",
        input_schema={"shape": [10]},
        output_schema={"shape": [10]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=0.05, max_absolute_error=0.1),
        resource_budget=ResourceBudget(max_memory_mb=256.0),
    )

    ref = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    cand_nan = np.array([1.0, np.nan, 3.0], dtype=np.float32)
    cand_inf = np.array([1.0, np.inf, 3.0], dtype=np.float32)

    passed, _, _, reason = differential_contract_verify(contract, cand_nan, ref)
    assert passed is False
    assert "NaN or Inf" in reason

    passed, _, _, reason = differential_contract_verify(contract, cand_inf, ref)
    assert passed is False
    assert "NaN or Inf" in reason


def test_contract_shape_mismatch_rejection():
    contract = UniversalContract(
        workload_id="matrix_op",
        category="linear_algebra",
        description="Matrix operation",
        input_schema={"shape": [4, 4]},
        output_schema={"shape": [4, 4]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=1e-3, max_absolute_error=1e-3),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.zeros((4, 4), dtype=np.float32)
    cand_wrong_shape = np.zeros((4, 5), dtype=np.float32)

    passed, _, _, reason = differential_contract_verify(contract, cand_wrong_shape, ref)
    assert passed is False
    assert "Shape mismatch" in reason
