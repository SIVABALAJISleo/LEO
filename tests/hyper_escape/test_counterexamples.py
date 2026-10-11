"""
tests/hyper_escape/test_counterexamples.py
Validates Automated Counterexample and Failure Discovery (Feature K / Section 13).
Challenges optimization candidates against adversarial inputs, boundary values,
and property-based invariants.
"""
import pytest
import numpy as np

from hyper_universal.contracts.contract_engine import (
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
    differential_contract_verify,
)
from hyper_universal.precision.optimizer import PrecisionOptimizer


def test_adversarial_dynamic_range_rejection():
    # Int8 quantization fails when values span extreme dynamic ranges (-1e6 to +1e6)
    contract = UniversalContract(
        workload_id="gemm_strict",
        category="linear_algebra",
        description="Strict contract for dynamic range",
        input_schema={"shape": [100]},
        output_schema={"shape": [100]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=0.01, max_absolute_error=0.05),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    # Adversarial input with an outlier
    data = np.ones(100, dtype=np.float32)
    data[0] = 1000.0  # massive outlier compressing dynamic range of int8

    optimizer = PrecisionOptimizer()
    quantized, scale, ev = optimizer.quantize_int8(data)
    dequantized = quantized.astype(np.float32) * scale

    passed, max_rel, max_abs, reason = differential_contract_verify(contract, dequantized, data)
    # Must fail because int8 quantization error across this outlier violates 0.05 absolute error!
    assert passed is False
    assert "exceeds contract tolerance" in reason


def test_boundary_values_empty_and_single_element():
    contract = UniversalContract(
        workload_id="vector_norm",
        category="linear_algebra",
        description="Vector norm on single element",
        input_schema={"shape": [1]},
        output_schema={"shape": [1]},
        exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
        tolerance=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    single = np.array([42.0], dtype=np.float32)
    passed, _, _, _ = differential_contract_verify(contract, single, single)
    assert passed is True


def test_counterexample_subnormal_numbers():
    contract = UniversalContract(
        workload_id="subnormal_check",
        category="scientific",
        description="Check subnormal floating point numbers",
        input_schema={"shape": [2]},
        output_schema={"shape": [2]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=1e-3, max_absolute_error=1e-6),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.array([1e-38, 1e-38], dtype=np.float32)
    # If a candidate flushes to zero:
    cand_flushed = np.array([0.0, 0.0], dtype=np.float32)

    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand_flushed, ref)
    # Relative error is 1.0 (100%), which exceeds 1e-3 -> FAIL
    assert passed is False
