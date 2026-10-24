"""
tests/test_candidate_workloads_15.py
====================================
Comprehensive Test Suite for the 15 Canonical Candidate Workloads.
Validates:
1. All 15 Workload Contracts & Schemas.
2. Independent Reference vs. Candidate Execution Equivalence.
3. Exactness Classes (BIT_EXACT, INTEGER_EXACT, NUMERICALLY_EQUIVALENT).
4. Adversarial & Edge-Case Battery.
5. Multi-operand Cache Key Isolation.
6. Fail-closed rejection of corrupted candidates.
"""

import pytest
import numpy as np

from hyper.canonical.workload_registry import (
    CANONICAL_REGISTRY,
    CANONICAL_15_WORKLOAD_IDS,
    ExactnessClass,
)
from hyper.canonical.independent_reference import IndependentReferenceEngine
from hyper.canonical.candidate_compiler import CandidateCompiler
from hyper.canonical.verified_cache import VerifiedExactCache
from hyper.canonical.verification_state_machine import (
    StrictVerificationRunner,
    VerificationStatus,
)


class TestCanonical15CandidateWorkloads:
    """Verifies all 15 candidate workload implementations against independent textbook references."""

    def test_registry_contains_all_15_contracts(self):
        contracts = CANONICAL_REGISTRY.get_all_contracts()
        assert len(contracts) == 15
        for wid in CANONICAL_15_WORKLOAD_IDS:
            assert wid in contracts
            assert contracts[wid].workload_id == wid
            assert contracts[wid].exactness_class in ExactnessClass

    @pytest.mark.parametrize("workload_id", CANONICAL_15_WORKLOAD_IDS)
    def test_candidate_matches_independent_reference_on_typical_input(self, workload_id):
        contract = CANONICAL_REGISTRY.get(workload_id)
        assert contract is not None

        inputs = StrictVerificationRunner.generate_typical_inputs(workload_id, seed=42)

        # 1. Independent Reference execution
        ref_out, ref_rec = IndependentReferenceEngine.execute_reference(workload_id, inputs)
        assert ref_out is not None
        assert ref_rec.is_independent is True

        # 2. Candidate execution
        cand_out, cand_rec = CandidateCompiler.execute_candidate(workload_id, inputs, contract=contract)
        assert cand_rec.is_success is True

        # 3. Contract exactness compliance check
        ok, msg, _ = contract.check_output_compliance(cand_out, ref_out)
        assert ok is True, f"Workload '{workload_id}' failed contract compliance: {msg}"

    @pytest.mark.parametrize("workload_id", CANONICAL_15_WORKLOAD_IDS)
    def test_candidate_passes_adversarial_battery(self, workload_id):
        contract = CANONICAL_REGISTRY.get(workload_id)
        adv_cases = StrictVerificationRunner.generate_adversarial_cases(workload_id, seed=142)
        assert len(adv_cases) > 0, f"Workload '{workload_id}' must define at least 1 adversarial case"

        for case_name, adv_inputs in adv_cases:
            ref_out, _ = IndependentReferenceEngine.execute_reference(workload_id, adv_inputs)
            cand_out, cand_rec = CandidateCompiler.execute_candidate(workload_id, adv_inputs, contract=contract)
            assert cand_rec.is_success is True, f"Candidate failed on adversarial case '{case_name}': {cand_rec.error_trace}"

            ok, msg, _ = contract.check_output_compliance(cand_out, ref_out)
            assert ok is True, f"Adversarial case '{case_name}' failed for '{workload_id}': {msg}"


class TestSafetyAndVerificationGates:
    """Verifies fail-closed behavior, cache isolation, and faulty candidate rejection."""

    def test_fail_closed_rejection_of_corrupted_candidate(self):
        contract = CANONICAL_REGISTRY.get("GEMM_STANDARD")
        inputs = StrictVerificationRunner.generate_typical_inputs("GEMM_STANDARD", seed=99)
        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)

        # Corrupt the output
        corrupted_output = ref_out + 5.0
        ok, status_msg, _ = contract.check_output_compliance(corrupted_output, ref_out)
        assert ok is False
        assert "FAIL" in status_msg

    def test_multi_operand_cache_integrity(self):
        cache = VerifiedExactCache(max_entries=10)
        A = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        B1 = np.array([[5.0], [6.0]], dtype=np.float32)
        B2 = np.array([[5.0], [7.0]], dtype=np.float32)  # Single element changed

        key1 = cache.compute_cache_key("GEMM_STANDARD", {"A": A, "B": B1})
        key2 = cache.compute_cache_key("GEMM_STANDARD", {"A": A, "B": B2})

        # Cache keys must strictly differ
        assert key1 != key2

        res1 = A @ B1
        cache.put(key1, "GEMM_STANDARD", res1, is_verified=True)

        # Lookup with key1 hits, lookup with key2 misses
        cached_val, hit, _ = cache.get(key1)
        assert hit is True
        np.testing.assert_array_equal(cached_val, res1)

        cached_val2, hit2, _ = cache.get(key2)
        assert hit2 is False
        assert cached_val2 is None

    def test_strict_verification_engine_reports_15_of_15(self):
        report = StrictVerificationRunner.verify_all_canonical_workloads(seed=42, prefer_igpu=True)
        assert report.total_workloads == 15
        assert report.pass_count == 15
        assert report.fail_count == 0
        assert report.unknown_count == 0
        assert report.blocked_count == 0
        assert report.is_15_of_15_verified is True
