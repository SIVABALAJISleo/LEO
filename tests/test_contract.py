import numpy as np
import pytest

from hyper.discovery.contract import (
     ContractAuditResult,
     InputDomainSpec,
     VerificationMode,
     WorkloadContract,
)


def test_contract_bit_exact_pass_and_fail():
    contract = WorkloadContract(
        contract_id="c_bit_exact_test",
        workload_name="gemm_exact",
        required_outputs=["result"],
        exactness_mode=VerificationMode.MODE_1_BIT_EXACT,
    )

    ref = {"result": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)}
    cand_exact = {"result": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)}
    cand_diff = {"result": np.array([[1.0, 2.0], [3.0, 4.00001]], dtype=np.float32)}

    # Pass case
    audit_pass = contract.verify(cand_exact, ref, runtime_ms=5.0)
    assert audit_pass.passed is True
    assert audit_pass.is_bit_exact is True
    assert audit_pass.parity_classification == "BIT_EXACT_COMPUTE_PARITY"

    # Fail case
    audit_fail = contract.verify(cand_diff, ref, runtime_ms=5.0)
    assert audit_fail.passed is False
    assert audit_fail.is_bit_exact is False
    assert audit_fail.parity_classification == "NO_BIT_EXACT_PARITY"


def test_contract_numeric_tolerance_classification_rule():
    """Scientific rule: Never label MODE 3 (tolerance) as bit-exact parity!"""
    contract = WorkloadContract(
        contract_id="c_tolerance_test",
        workload_name="approx_gemm",
        required_outputs=["Y"],
        exactness_mode=VerificationMode.MODE_3_NUMERIC_TOLERANCE,
        tolerance_atol=1e-3,
        tolerance_rtol=1e-3,
    )

    ref = {"Y": np.array([1.0, 2.0, 3.0], dtype=np.float32)}
    cand = {"Y": np.array([1.0002, 1.9998, 3.0001], dtype=np.float32)}

    audit = contract.verify(cand, ref, runtime_ms=2.0)
    assert audit.passed is True
    # Must NOT be labeled as BIT_EXACT_COMPUTE_PARITY
    assert audit.parity_classification == "NUMERICAL_PARITY"
    assert audit.parity_classification != "BIT_EXACT_COMPUTE_PARITY"


def test_contract_resource_and_prohibition_violations():
    contract = WorkloadContract(
        contract_id="c_limits_test",
        workload_name="latency_sensitive",
        required_outputs=["out"],
        max_latency_ms=10.0,
        max_memory_mb=50.0,
        prohibit_external_compute=True,
    )

    ref = {"out": 42}
    cand = {"out": 42}

    # Latency violation
    audit_lat = contract.verify(cand, ref, runtime_ms=15.0, memory_mb=10.0)
    assert audit_lat.passed is False
    assert any("Latency violation" in v for v in audit_lat.violations)

    # Memory violation
    audit_mem = contract.verify(cand, ref, runtime_ms=5.0, memory_mb=80.0)
    assert audit_mem.passed is False
    assert any("Memory violation" in v for v in audit_mem.violations)

    # Prohibited external compute
    audit_ext = contract.verify(cand, ref, runtime_ms=5.0, candidate_external_compute_detected=True)
    assert audit_ext.passed is False
    assert any("External network or prohibited hardware" in v for v in audit_ext.violations)
