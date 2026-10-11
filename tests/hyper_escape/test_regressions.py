"""
tests/hyper_escape/test_regressions.py
Validates Historical Regressions and Integrity Invariants (Phase 1 & 10).
Guarantees that previously identified defects (e.g. disjunctive tolerance leakage,
synthetic bandwidth reporting, division by zero) do not reappear.
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
from hyper_universal.certification.engine import FormalCertificationEngine


def test_regression_disjunctive_tolerance_prevented():
    """
    CRITICAL REGRESSION CHECK:
    In previous buggy iterations, a disjunctive 'or' was used:
    (max_rel <= tol_rel) or (max_abs <= tol_abs)
    which allowed candidates with 10,000% error to pass simply because max_abs was small on tiny numbers.
    Verification MUST be strictly conjunctive 'and'.
    """
    contract = UniversalContract(
        workload_id="strict_conjunctive",
        category="linear_algebra",
        description="Verify strict conjunctive check",
        input_schema={"shape": [2]},
        output_schema={"shape": [2]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=0.01, max_absolute_error=0.01),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    # Reference = [100.0, 100.0]
    ref = np.array([100.0, 100.0], dtype=np.float32)
    # Cand has max_rel = 0.005 (<= 0.01), BUT max_abs = 0.5 (> 0.01)
    cand = np.array([100.5, 100.0], dtype=np.float32)

    passed, max_rel, max_abs, reason = differential_contract_verify(contract, cand, ref)
    # MUST FAIL: max_abs (0.5) exceeds max_abs_err (0.01)
    assert passed is False
    assert "exceeds contract tolerance" in reason


def test_regression_zero_latency_speedup_safeguard():
    """Candidates reporting zero latency (e.g. timer underflow) must not crash with ZeroDivisionError."""
    certifier = FormalCertificationEngine()
    contract = UniversalContract(
        workload_id="speedup_zero",
        category="misc",
        description="Speedup divide by zero guard",
        input_schema={"shape": [1]},
        output_schema={"shape": [1]},
        exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        tolerance=NumericalTolerance(max_relative_error=0.1, max_absolute_error=0.1),
        resource_budget=ResourceBudget(max_memory_mb=64.0),
    )

    ref = np.array([1.0], dtype=np.float32)
    cand = np.array([1.0], dtype=np.float32)

    # 0.0 latency passed in
    cert = certifier.certify_candidate(
        candidate_id="zero_timer_cand",
        contract=contract,
        candidate_output=cand,
        reference_output=ref,
        candidate_latency_ms=0.0,
        reference_latency_ms=1.0,
        backend_name="CPU_AVX2",
    )

    # Must be clamped or handled without exception
    assert cert.speedup >= 1.0
