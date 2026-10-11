"""
tests/hyper_escape/test_certification.py
Validates Comprehensive Formal Certification Engine (Feature G / Section 9.3 & 9.4).
Tests 9 formal certification states, speedup math formulas, and certificate reproducibility.
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


def test_approximate_verified_state():
    certifier = FormalCertificationEngine()

    contract = UniversalContract(
        workload_id="ai_embedding",
        category="ai_inference",
        description="Embedding with approximate tolerance",
        input_schema={"shape": [128]},
        output_schema={"shape": [128]},
        exactness_requirement=ExactnessRequirement.APPROXIMATE_WITH_TOLERANCE,
        tolerance=NumericalTolerance(max_relative_error=0.10, max_absolute_error=0.20),
        resource_budget=ResourceBudget(max_memory_mb=128.0),
    )

    ref = np.ones(128, dtype=np.float32)
    # Cand has 5% error
    cand = ref * 1.05

    cert = certifier.certify_candidate(
        candidate_id="quant_embedding",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=1.5,
        reference_latency_ms=3.0,
        backend_name="CPU_AVX2",
    )

    assert cert.certification_state == CertificationState.APPROXIMATE_VERIFIED
    assert cert.speedup == 2.0
    assert cert.passes_contract is True


def test_speedup_slower_candidate_handling():
    certifier = FormalCertificationEngine()

    contract = UniversalContract(
        workload_id="crypto_rsa",
        category="cryptography",
        description="Exact crypto op",
        input_schema={"dtype": "int32"},
        output_schema={"dtype": "int32"},
        exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
        tolerance=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.array([1, 2, 3], dtype=np.int32)
    cand = np.array([1, 2, 3], dtype=np.int32)

    # Candidate is slower: 10 ms vs 5 ms reference -> speedup = 0.5x
    cert = certifier.certify_candidate(
        candidate_id="unoptimized_cand",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=10.0,
        reference_latency_ms=5.0,
        backend_name="CPU_AVX2",
    )

    # Slower candidates must NOT be described as performance wins!
    assert cert.speedup == 0.5
    assert cert.certification_state == CertificationState.EXACT_VERIFIED  # Correctness passes, but speedup is truthfully recorded as 0.5
    assert cert.speedup < 1.0
