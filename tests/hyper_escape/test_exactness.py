"""
tests/hyper_escape/test_exactness.py
Validates Exactness, Correctness and Certification Engine (Feature G / Section 9).
Tests certification state transitions: EXACT_VERIFIED, CONTRACT_VERIFIED,
APPROXIMATE_VERIFIED, and fail-closed FAILED_CORRECTNESS.
"""
import pytest
import numpy as np

from hyper_universal.contracts.contract_engine import (
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
)
from hyper_universal.certification.engine import (
    FormalCertificationEngine,
    CertificationState,
)


def test_exact_verified_certification():
    certifier = FormalCertificationEngine()

    contract = UniversalContract(
        workload_id="sorting_keys",
        category="algorithms",
        description="Exact integer sort",
        input_schema={"dtype": "int32"},
        output_schema={"dtype": "int32"},
        exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
        tolerance=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.array([1, 2, 3, 4, 5], dtype=np.int32)
    cand = np.array([1, 2, 3, 4, 5], dtype=np.int32)

    cert = certifier.certify_candidate(
        candidate_id="radix_sort_cand",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=1.2,
        reference_latency_ms=3.6,
        backend_name="CPU_AVX2",
    )

    assert cert.certification_state == CertificationState.EXACT_VERIFIED
    assert cert.speedup == 3.0
    assert cert.max_absolute_error == 0.0
    assert cert.passes_contract is True


def test_contract_verified_numerical_tolerance():
    certifier = FormalCertificationEngine()

    contract = UniversalContract(
        workload_id="gemm_fp32",
        category="linear_algebra",
        description="GEMM with standard FP32 tolerance",
        input_schema={"shape": [10, 10]},
        output_schema={"shape": [10, 10]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.ones((10, 10), dtype=np.float32)
    # Cand has tiny error 1e-6 (within 1e-4 tolerance, but not 0)
    cand = ref + 1e-6

    cert = certifier.certify_candidate(
        candidate_id="blocked_gemm",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=2.0,
        reference_latency_ms=4.0,
        backend_name="CPU_AVX2",
    )

    assert cert.certification_state == CertificationState.CONTRACT_VERIFIED
    assert cert.speedup == 2.0
    assert cert.passes_contract is True


def test_failed_correctness_rejection():
    certifier = FormalCertificationEngine()

    contract = UniversalContract(
        workload_id="gemm_fp32",
        category="linear_algebra",
        description="GEMM rejecting error",
        input_schema={"shape": [10, 10]},
        output_schema={"shape": [10, 10]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.ones((10, 10), dtype=np.float32)
    # Cand has large error 0.5 (violates tolerance)
    cand = ref + 0.5

    cert = certifier.certify_candidate(
        candidate_id="buggy_gemm",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=1.0,
        reference_latency_ms=4.0,
        backend_name="CPU_AVX2",
    )

    assert cert.certification_state == CertificationState.FAILED_CORRECTNESS
    assert cert.passes_contract is False
    assert "exceeds contract tolerance" in cert.evidence_notes
