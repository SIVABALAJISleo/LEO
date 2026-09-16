#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_verification_foundation.py
=====================================
Comprehensive Test Suite for Phase 1 Fail-Closed Verification Subsystem.
Tests all 14 modular verifiers:
  1. ContractVerifier
  2. ExactVerifier
  3. NumericalVerifier
  4. OutputHashVerifier
  5. OperationTraceVerifier
  6. ProvenanceVerifier
  7. BenchmarkIntegrityVerifier
  8. CacheIntegrityVerifier
  9. IndependentVerifier
  10. AdversarialVerifier
  11. HoldoutVerifier
  12. RealtimeVerifier
  13. ResourceVerifier
  14. CertificationEngine
"""

import numpy as np
import pytest

from hyper_x.contract import WorkloadContract
from hyper_x.verification.contract_verifier import ContractVerifier
from hyper_x.verification.exact_verifier import ExactVerifier
from hyper_x.verification.numerical_verifier import NumericalVerifier
from hyper_x.verification.output_hash_verifier import OutputHashVerifier
from hyper_x.verification.operation_trace_verifier import OperationTraceVerifier
from hyper_x.verification.provenance_verifier import ProvenanceVerifier
from hyper_x.verification.benchmark_integrity import BenchmarkIntegrityVerifier
from hyper_x.verification.cache_integrity import CacheIntegrityVerifier
from hyper_x.verification.independent_verifier import IndependentVerifier
from hyper_x.verification.adversarial_verifier import AdversarialVerifier
from hyper_x.verification.holdout_verifier import HoldoutVerifier
from hyper_x.verification.realtime_verifier import RealtimeVerifier
from hyper_x.verification.resource_verifier import ResourceVerifier
from hyper_x.verification.certification_engine import CertificationEngine


def test_contract_verifier():
    contract = WorkloadContract(
        workload_id="gemm_test",
        workload_domain="DENSE_LINEAR_ALGEBRA",
        input_schema={"type": "tensor", "shape": [512, 512]},
        input_hash="a" * 64,
        output_schema={"type": "tensor", "shape": [512, 512]},
        output_observable="FULL_TENSOR",
        correctness_class="EXACT_BIT_EQUAL",
        numerical_tolerance=0.0,
        bit_exact_required=True,
        latency_deadline_ms=50.0,
        memory_limit_mb=1024.0,
        external_compute_allowed=False,
    )
    valid_telemetry = {
        "external_compute_used": False,
        "cache_hit": False,
        "precomputed_used": False,
        "is_approximate": False,
        "peak_memory_mb": 256.0,
    }
    dummy_out = np.zeros((512, 512), dtype=np.float32)

    res = ContractVerifier.verify(contract, valid_telemetry, dummy_out)
    assert res.passed is True
    assert res.contract_hash != ""

    # Disallowed external compute triggers violation
    bad_telemetry = dict(valid_telemetry, external_compute_used=True)
    res_bad = ContractVerifier.verify(contract, bad_telemetry, dummy_out)
    assert res_bad.passed is False
    assert len(res_bad.violations) > 0


def test_exact_verifier():
    a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    b = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    c = np.array([1.0, 2.0, 3.0001], dtype=np.float32)

    res_pass = ExactVerifier.verify(a, b)
    assert res_pass.passed is True
    assert res_pass.is_bitwise_identical is True

    res_fail = ExactVerifier.verify(a, c)
    assert res_fail.passed is False
    assert res_fail.is_bitwise_identical is False


def test_numerical_verifier():
    ref = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    cand_close = np.array([1.00001, 2.00001, 2.99999], dtype=np.float32)
    cand_far = np.array([1.1, 2.0, 3.0], dtype=np.float32)

    assert NumericalVerifier.verify(cand_close, ref, rel_tolerance=1e-4, abs_tolerance=1e-4).passed is True
    assert NumericalVerifier.verify(cand_far, ref, rel_tolerance=1e-4, abs_tolerance=1e-4).passed is False


def test_output_hash_verifier():
    data = np.array([1, 2, 3, 4], dtype=np.int32)
    correct_hash = OutputHashVerifier.hash_output(data)

    assert OutputHashVerifier.verify(data, correct_hash).passed is True
    assert OutputHashVerifier.verify(data, "bad_hash_value").passed is False


def test_operation_trace_verifier():
    valid_trace = [
        {"id": "op_0", "dependencies": []},
        {"id": "op_1", "dependencies": ["op_0"]},
        {"id": "op_2", "dependencies": ["op_1"]},
    ]
    assert OperationTraceVerifier.verify_trace(valid_trace).passed is True

    invalid_trace = [
        {"id": "op_1", "dependencies": ["unseen_step"]},
    ]
    assert OperationTraceVerifier.verify_trace(invalid_trace).passed is False


def test_provenance_verifier():
    valid_prov = {
        "git_commit": "abcdef1234567890",
        "input_hash": "a" * 64,
        "model_hash": "b" * 64,
        "hardware_identity": "Intel Core i5-12450H",
        "seed": 42,
        "compiler_version": "3.13.5",
    }
    assert ProvenanceVerifier.verify(valid_prov).passed is True

    missing_prov = {
        "git_commit": "abcdef1234567890",
    }
    assert ProvenanceVerifier.verify(missing_prov).passed is False


def test_benchmark_integrity_verifier():
    def clean_code(x):
        return x * 2

    assert BenchmarkIntegrityVerifier.verify_callable(clean_code).passed is True

    def cheating_code(x):
        speedup = 999.0
        return speedup

    assert BenchmarkIntegrityVerifier.verify_callable(cheating_code).passed is False


def test_cache_integrity_verifier():
    res_cold = CacheIntegrityVerifier.verify("COLD_START", "COMPUTED", 1.0)
    assert res_cold.passed is True
    assert res_cold.is_cold_start_verified is True

    res_cached = CacheIntegrityVerifier.verify("EXACT_CACHE_HIT", "SPEEDUP_CLAIMED", 50.0)
    assert res_cached.passed is False


def test_independent_verifier():
    ref_obj = object()
    cand_obj = object()

    res = IndependentVerifier.verify(cand_obj, ref_obj, "cand_out", "ref_out")
    assert res.passed is True

    res_self = IndependentVerifier.verify(ref_obj, ref_obj, "same", "same")
    assert res_self.passed is False
    assert res_self.self_comparison_detected is True


def test_adversarial_verifier():
    ref_fn = lambda x: x * 2
    cand_fn = lambda x: x * 2
    inputs = [np.zeros(10), np.ones(10) * 1e6, np.full(10, -1.0)]
    comparator = lambda c, r: bool(np.allclose(c, r))

    res = AdversarialVerifier.verify(cand_fn, ref_fn, inputs, comparator)
    assert res.passed is True
    assert res.tests_executed == 3


def test_holdout_verifier():
    ref_fn = lambda x: x ** 2
    cand_fn = lambda x: x ** 2
    holdout = [np.array([1.0, 5.0]), np.array([-3.0, 4.0])]
    comparator = lambda c, r: bool(np.allclose(c, r))

    res = HoldoutVerifier.verify(cand_fn, ref_fn, holdout, comparator)
    assert res.passed is True
    assert res.samples_evaluated == 2


def test_realtime_verifier():
    samples_pass = [10.0, 11.2, 9.8, 12.0, 14.5]
    res_pass = RealtimeVerifier.verify(samples_pass, deadline_ms=16.67)
    assert res_pass.passed is True

    samples_fail = [10.0, 11.2, 19.5, 12.0, 14.5]
    res_fail = RealtimeVerifier.verify(samples_fail, deadline_ms=16.67)
    assert res_fail.passed is False
    assert res_fail.deadline_violations > 0


def test_resource_verifier():
    res_pass = ResourceVerifier.verify([100.0, 150.0, 120.0, 140.0], memory_limit_mb=1024.0, thermal_throttle_flag=False)
    assert res_pass.passed is True

    res_throttled = ResourceVerifier.verify([100.0, 150.0], memory_limit_mb=1024.0, thermal_throttle_flag=True)
    assert res_throttled.passed is False


def test_certification_engine_full_loop():
    contract = WorkloadContract(
        workload_id="omega_cert_gemm",
        workload_domain="DENSE_LINEAR_ALGEBRA",
        input_schema={"type": "tensor", "shape": [512, 512]},
        input_hash="a" * 64,
        output_schema={"type": "tensor", "shape": [512, 512]},
        output_observable="FULL_TENSOR",
        correctness_class="EXACT_BIT_EQUAL",
        numerical_tolerance=0.0,
        bit_exact_required=True,
        latency_deadline_ms=50.0,
        memory_limit_mb=1024.0,
    )

    arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    contract_res = ContractVerifier.verify(contract, {"peak_memory_mb": 128.0}, arr)
    exact_res = ExactVerifier.verify(arr, arr)
    hash_val = OutputHashVerifier.hash_output(arr)
    output_hash_res = OutputHashVerifier.verify(arr, hash_val)
    trace_res = OperationTraceVerifier.verify_trace([{"id": "root", "dependencies": []}])
    prov_res = ProvenanceVerifier.verify({
        "git_commit": "abc",
        "input_hash": "a" * 64,
        "model_hash": "b" * 64,
        "hardware_identity": "Intel Core i5-12450H",
        "seed": 42,
        "compiler_version": "3.13.5",
    })
    integ_res = BenchmarkIntegrityVerifier.verify_callable(lambda x: x)
    cache_res = CacheIntegrityVerifier.verify("COLD_START", "COMPUTED", 1.0)
    indep_res = IndependentVerifier.verify(object(), object(), "cand", "ref")
    adv_res = AdversarialVerifier.verify(lambda x: x, lambda x: x, [1, 2], lambda c, r: c == r)
    hold_res = HoldoutVerifier.verify(lambda x: x, lambda x: x, [1, 2], lambda c, r: c == r)
    real_res = RealtimeVerifier.verify([5.0, 6.0], deadline_ms=50.0)
    res_res = ResourceVerifier.verify([100.0, 120.0], memory_limit_mb=1024.0, thermal_throttle_flag=False)

    report = CertificationEngine.certify(
        contract=contract,
        contract_res=contract_res,
        numerical_or_exact_res=exact_res,
        output_hash_res=output_hash_res,
        trace_res=trace_res,
        provenance_res=prov_res,
        integrity_res=integ_res,
        cache_res=cache_res,
        independent_res=indep_res,
        adversarial_res=adv_res,
        holdout_res=hold_res,
        realtime_res=real_res,
        resource_res=res_res,
    )

    assert report.is_certified is True
    assert report.rtx_equivalent_gate is True
    assert report.universal_100_gate is True
    assert report.certification_status == "VERIFIED"
    assert report.certificate_hash != ""
