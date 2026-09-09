"""
tests/test_cco_verification.py
==============================
Tests for Verification Suite, Cryptographic Certificates, and Decoupled Scorecard:
- Freivalds O(N^2) randomized matrix multiplication verifier (detection of subtle single-element corruptions)
- ExecutionCertificate sealing and tamper detection
- DecoupledParityScorecard truthfulness (0.0% physical hardware parity vs application parity)
"""

import pytest
import numpy as np
from hyper_cco.verifier import CcoVerifier, VerificationStatus
from hyper_cco.certificate import ExecutionCertificate, CertificateLedger
from hyper_cco.contract import ExactnessClass
from hyper_cco.scorecard import ScorecardBuilder, DecoupledParityScorecard


def test_freivalds_verifier_passes_on_correct_matmul():
    N = 64
    A = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)
    C_correct = A @ B

    status, confidence, details = CcoVerifier.verify_freivalds(A, B, C_correct, rounds=15)
    assert status == VerificationStatus.PASS
    assert confidence > 0.9999
    assert details["rounds_passed"] == 15


def test_freivalds_verifier_catches_single_element_corruption():
    N = 64
    A = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)
    C_corrupted = A @ B
    # Corrupt single scalar
    C_corrupted[12, 15] += 0.5

    status, confidence, details = CcoVerifier.verify_freivalds(A, B, C_corrupted, rounds=15, tolerance=1e-4)
    assert status == VerificationStatus.FAIL
    assert "Freivalds" in details["reason"]


def test_certificate_sealing_and_tamper_detection():
    ledger = CertificateLedger()
    cert = ledger.issue_certificate(
        workload_id="CERT_TEST",
        input_hash="hash_123",
        contract_hash="contract_456",
        strategy="EXACT_CACHE",
        exactness_class=ExactnessClass.CACHED,
        original_work=1000.0,
        executed_work=0.0,
        latency_ms=0.5,
        error_abs=0.0,
        error_rel=0.0,
        device="CACHE_MEMORY",
        verification_status=VerificationStatus.PASS,
        verification_method="FREIVALDS_O(N^2)"
    )

    # 1. Verification of untampered certificate
    assert cert.verify_integrity() is True

    # 2. Tampering test: artificially modify latency or work
    cert.latency_ms = 0.001
    assert cert.verify_integrity() is False, "Tampered certificate failed to flag modification!"


def test_scorecard_truthful_rejection_of_silicon_gate():
    scorecard = ScorecardBuilder.build_scorecard_from_execution(
        workload_id="GEMM_SCORECARD_TEST",
        work_elimination=0.70,
        measured_speedup=1.25,
        numerical_error=4e-7,
        contract_satisfied=True,
        verification_status=VerificationStatus.PASS
    )

    # Application parity is satisfied
    assert scorecard.application_parity_pct == 96.0
    # Raw hardware parity is 0.0% (intel UHD lacks physical CUDA cores)
    assert scorecard.raw_hardware_parity_pct == 0.0
    # Conjunctive 100% gate must FAIL truthfully
    assert scorecard.conjunctive_100_gate_passed is False
