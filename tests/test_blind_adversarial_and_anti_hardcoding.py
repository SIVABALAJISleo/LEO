"""
tests/test_blind_adversarial_and_anti_hardcoding.py
===================================================
Validation suite for Phase 11 (Blind & Adversarial Testing) & Phase 12 (Anti-Hardcoding System).
"""

import time
import numpy as np
import pytest

from hyper.research_engine.anti_cheat_and_holdout import (
    AntiHardcodingEngine,
    BlindWorkloadRunner,
    ClaimValidator,
    WorkloadCategory,
    WorkloadGenerator,
)
from hyper.research_engine.contracts import ComputationalContract


def test_workload_generator_multidomain():
    categories = [
        WorkloadCategory.LINEAR_ALGEBRA,
        WorkloadCategory.MATHEMATICS,
        WorkloadCategory.SORTING,
        WorkloadCategory.DYNAMIC_PROGRAMMING,
        WorkloadCategory.CRYPTOGRAPHIC_PRIMITIVES,
        WorkloadCategory.SIGNAL_PROCESSING,
        WorkloadCategory.IMAGE_PROCESSING,
    ]

    for cat in categories:
        contract, inputs, ref_out, ref_fn = WorkloadGenerator.generate_unseen_workload(cat, seed=42)
        assert isinstance(contract, ComputationalContract)
        assert len(inputs) > 0
        computed = ref_fn(inputs)
        ok, msg, err = contract.validate_output(computed, ref_out)
        assert ok is True


def test_blind_workload_runner_evaluation():
    contract, inputs, ref_out, ref_fn = WorkloadGenerator.generate_unseen_workload(
        WorkloadCategory.LINEAR_ALGEBRA, seed=123
    )

    # Simulated blind search engine discovering an exact matmul pathway
    def mock_blind_search(blind_contract):
        def pathway_exec(inp):
            return inp["A"] @ inp["B"]
        return pathway_exec

    result = BlindWorkloadRunner.execute_blind_evaluation(
        contract=contract,
        inputs=inputs,
        reference_fn=ref_fn,
        search_engine_fn=mock_blind_search,
    )

    assert result["status"] == "PASS"
    assert result["is_verified_blind"] is True
    assert "ANON_TASK_" in result["blind_task_id"]
    assert result["max_difference"] <= contract.tolerance_epsilon


def test_anti_hardcoding_audits():
    # 1. Clean algorithmic function
    def clean_matmul(inputs):
        return inputs["A"] @ inputs["B"]

    is_clean, findings = AntiHardcodingEngine.audit_callable(clean_matmul)
    assert is_clean is True

    # 2. Hardcoded sleep cheat
    def sleep_cheat(inputs):
        time.sleep(0.01)
        return inputs["A"]

    is_clean_sleep, findings_sleep = AntiHardcodingEngine.audit_callable(sleep_cheat)
    assert is_clean_sleep is False
    assert any("sleep" in f.lower() for f in findings_sleep)

    # 3. Hardcoded benchmark name comparison cheat
    def name_branch_cheat(inputs, name="benchmark_test"):
        if name == "benchmark_test":
            return 42
        return 0

    is_clean_branch, findings_branch = AntiHardcodingEngine.audit_callable(name_branch_cheat)
    assert is_clean_branch is False
    assert any("benchmark" in f.lower() for f in findings_branch)


def test_claim_validator_prevents_false_claims():
    # Test rejection of 100% universal parity with incomplete exact coverage
    valid, reason, c_type = ClaimValidator.validate_claim(
        statement="Achieved 100% Universal Parity on All Datasets",
        exact_coverage=0.267,
        contract_coverage=1.0,
        hardware_parity_claimed=False,
    )
    assert valid is False
    assert "REJECTED" in reason
    assert c_type == "HYPOTHESIS"

    # Test rejection of physical hardware parity claim
    valid_hw, reason_hw, c_type_hw = ClaimValidator.validate_claim(
        statement="100% hardware parity with RTX 5090",
        exact_coverage=1.0,
        contract_coverage=1.0,
        hardware_parity_claimed=True,
    )
    assert valid_hw is False
    assert "Physically Disjoint" in reason_hw

    # Test acceptance of modest measured claim
    valid_meas, reason_meas, c_type_meas = ClaimValidator.validate_claim(
        statement="1.96x measured speedup on MLP inference",
        exact_coverage=0.267,
        contract_coverage=1.0,
        hardware_parity_claimed=False,
    )
    assert valid_meas is True
    assert c_type_meas == "MEASURED_RESULT"
