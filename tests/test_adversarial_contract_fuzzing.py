"""
tests/test_adversarial_contract_fuzzing.py
==========================================
Unit tests for Mechanism 8: Adversarial Contract Fuzzing Engine.
Asserts that the invariant `accepted_result => measured_contract_satisfied` is strictly preserved.
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass
from hyper_cco.adversarial_fuzzer import (
    AdversarialContractFuzzer,
    FailureMode,
    FuzzAttackResult
)


def test_adversarial_silent_degradation_detected():
    fuzzer = AdversarialContractFuzzer()
    contract = ComputeContract(
        workload_id="FUZZ_SILENT_TEST",
        max_absolute_error=1e-3
    )

    def exact_fn(x):
        return x * 2.0

    # Vulnerable candidate that accepts corrupt output
    def bad_candidate(x):
        return x * 2.0 + 0.1, True, {}  # 0.1 > 1e-3

    res = fuzzer.test_silent_accuracy_degradation(bad_candidate, exact_fn, contract)
    # The fuzzer should detect that the bad candidate violated the contract
    assert res.invariant_preserved is False
    assert res.measured_error > contract.max_absolute_error

    # Safe candidate that validates against contract and rejects
    def safe_candidate(x):
        cand = x * 2.0 + 0.1
        err = np.max(np.abs(cand - exact_fn(x)))
        if err > contract.max_absolute_error:
            return exact_fn(x), False, {"fallback": True}
        return cand, True, {}

    res_safe = fuzzer.test_silent_accuracy_degradation(safe_candidate, exact_fn, contract)
    assert res_safe.invariant_preserved is True
    assert res_safe.fallback_engaged is True


def test_adversarial_cache_poisoning_defense():
    fuzzer = AdversarialContractFuzzer()
    cache_store = {}

    def store(k, key_data, val):
        # Secure cache verifies key content hash and refuses to overwrite if already stored with different value
        kh = hash(key_data.tobytes())
        if k not in cache_store:
            cache_store[k] = (kh, val)
        elif not np.allclose(cache_store[k][1], val):
            # Attempted poisoning detected! Refuse to overwrite authentic entry
            pass

    def lookup(k, key_data):
        if k in cache_store:
            stored_h, val = cache_store[k]
            if stored_h == hash(key_data.tobytes()):
                return True, val
        return False, None

    def verify(retrieved, original):
        if retrieved is None:
            return False
        return np.allclose(retrieved, original)

    res = fuzzer.test_cache_poisoning(store, lookup, verify)
    assert res.invariant_preserved is True


def test_adversarial_numerical_instability():
    fuzzer = AdversarialContractFuzzer()
    contract = ComputeContract(
        workload_id="FUZZ_NUM_TEST",
        max_absolute_error=1e-3
    )

    def exact_fn(H):
        return np.linalg.pinv(H)

    def safe_candidate(H):
        # Detect ill-conditioned matrix: condition number > 1e6 in FP32 indicates extreme instability
        cond = np.linalg.cond(H)
        if cond > 1e6:
            return exact_fn(H), False  # Reject and fallback
        return exact_fn(H), True

    res = fuzzer.test_numerical_instability(safe_candidate, exact_fn, contract)
    assert res.invariant_preserved is True
    assert res.fallback_engaged is True
