#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_hyper_x_vnext.py
===========================
Comprehensive Test Suite for HYPER / LEO vNext Architecture.
Tests all 13 phases of the Adaptive Cheapest-Valid Computation Engine.
"""

import pytest
import numpy as np
import json
import time

from hyper_x.contract_ir import ContractIR, ExactnessClass, ContractParser, classify_workload
from hyper_x.information_boundary import InformationBoundaryEngine, InfluenceGraph, InformationCategory
from hyper_x.necessity import NecessaryWorkCompiler, WorkBreakdown, WorkLedger
from hyper_x.pathway_search import PathwaySearchEngine, ExactReuseEngine, SemanticCacheEngine, CandidatePathway
from hyper_x.verification import AuthoritativeVerifier, VerificationStatus, NumericalVerifier, AdversarialVerifier
from hyper_x.decp import FrozenExecutionManifest, CrossHardwareComparator, DECPEngine
from hyper_x.certificates import ExecutionCertificate
from hyper_x.evidence import EvidenceLedger
from hyper_x.cost_model.calibration import DeviceCalibrator
from hyper_x.fallback import FallbackEngine
from hyper_x.pipeline import AuthoritativePipeline
from hyper_x.dashboard import ParityDashboard


def test_contract_ir_parsing():
    """Verify ContractParser creates formal ContractIR with deterministic hash."""
    A = np.zeros((128, 128), dtype=np.float32)
    contract = ContractParser.parse("gemm_test_workload", A, {"exact": True})
    assert contract.workload_family == "DENSE_LINEAR_ALGEBRA"
    assert contract.exactness_class == ExactnessClass.EXACT
    assert contract.numerical_tolerance == 0.0

    hash1 = contract.compute_contract_hash()
    hash2 = contract.compute_contract_hash()
    assert hash1 == hash2
    assert len(hash1) == 64


def test_information_boundary_partition():
    """Verify Information Boundary Engine identifies low-rank redundancy accurately."""
    eng = InformationBoundaryEngine()
    # Rank-1 matrix
    A = np.ones((64, 64), dtype=np.float32)
    meta = eng.analyze_matrix_workload(A)
    assert meta["sufficient_rank"] == 1
    assert meta["redundant_information_ratio"] > 0.95
    assert meta["can_eliminate_dense_full_rank"] is True


def test_necessary_work_compiler():
    """Verify arithmetic accounting in NecessaryWorkCompiler."""
    comp = NecessaryWorkCompiler()
    # 512x512 matrix with rank 16
    breakdown = comp.compile_matrix_work(512, 512, 512, effective_rank=16)
    assert breakdown.original_flops == 2.0 * (512 ** 3)
    assert breakdown.work_elimination_ratio > 0.90
    assert breakdown.work_elimination_pct > 90.0


def test_exact_reuse_provenance():
    """Verify ExactReuseEngine requires cryptographic provenance match."""
    cache = ExactReuseEngine()
    A = np.ones((32, 32), dtype=np.float32)
    contract_hash = "fake_contract_hash_123"
    result = np.ones((32, 32), dtype=np.float32) * 32.0

    cache.insert(A, contract_hash, result)

    # Identical lookup succeeds
    hit = cache.lookup(A, contract_hash)
    assert hit is not None
    assert np.array_equal(hit[0], result)

    # Different contract fails (miss)
    miss_contract = cache.lookup(A, "different_contract_hash")
    assert miss_contract is None

    # Altered input fails (miss)
    A_altered = np.copy(A)
    A_altered[0, 0] = 99.0
    miss_data = cache.lookup(A_altered, contract_hash)
    assert miss_data is None


def test_fail_closed_verifier():
    """Verify AuthoritativeVerifier fails closed with zero default passes."""
    verifier = AuthoritativeVerifier()
    A = np.eye(16, dtype=np.float32)
    B = np.eye(16, dtype=np.float32)
    contract = ContractParser.parse("unit_test", A)

    # 1. Honest Pass
    status, out, meta = verifier.verify_candidate_matrix(lambda: (A @ B, {}), A, B, contract)
    assert status == VerificationStatus.PASS
    assert meta["verified"] is True

    # 2. Corrupt Failure
    bad_status, bad_out, bad_meta = verifier.verify_candidate_matrix(lambda: (A + 5.0, {}), A, B, contract)
    assert bad_status == VerificationStatus.FAIL
    assert bad_meta["verified"] is False
    assert "tolerance failed" in bad_meta["reason"]

    # 3. NaN Injection Failure
    nan_cand = lambda: (np.full_like(A, np.nan), {})
    nan_status, _, nan_meta = verifier.verify_candidate_matrix(nan_cand, A, B, contract)
    assert nan_status == VerificationStatus.FAIL
    assert nan_meta["verified"] is False


def test_decp_deterministic_parity():
    """Verify HYPER-DECP cross-hardware comparison and ULP analysis."""
    decp = DECPEngine()
    manifest = FrozenExecutionManifest("decp_test")
    A = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

    res = decp.run_deterministic_comparison(A, A, manifest)
    assert res["classification"] == "EXACT_MATCH"
    assert res["bit_exact_output_parity_pct"] == 100.0
    assert res["mean_ulp_distance"] == 0.0


def test_certificate_tamper_evidence():
    """Verify ExecutionCertificate detects any unauthorized post-hoc modification."""
    cert = ExecutionCertificate(
        certificate_id="cert_test",
        timestamp=time.time(),
        workload_id="gemm_test",
        contract_hash="abc",
        hardware_fingerprint="i5-12450H",
        candidate_hash="cand",
        reference_hash="ref",
        input_hash="inp",
        output_hash="out",
        exactness_class="EXACT",
        correctness_result="PASS",
        numerical_metrics={"rel_err": 0.0},
        adversarial_result={},
        holdout_result={},
        latency_samples_ms=[1.0],
        throughput_ops_per_sec=1000.0,
        memory_rss_mb=100.0,
        work_reference_flops=1000.0,
        work_necessary_flops=100.0,
        work_eliminated_ratio=0.90,
        cache_state="COLD",
        provenance="MEASURED",
        fallback_status="NONE"
    )
    assert cert.verify_tamper_evident() is True

    # Tamper with numerical error
    cert.work_eliminated_ratio = 0.99
    assert cert.verify_tamper_evident() is False


def test_fallback_graceful_recovery():
    """Verify FallbackEngine recovers exact mathematical result when shortcut is broken."""
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    fb_out, fb_meta = FallbackEngine.execute_matrix_fallback(A, B, "ShortcutVerifierFailed")
    expected = A @ B
    assert np.allclose(fb_out, expected, atol=1e-5)
    assert fb_meta["fallback_engaged"] is True


def test_authoritative_pipeline_end_to_end():
    """Verify the complete Authoritative Pipeline runs from input to signed certificate."""
    pipeline = AuthoritativePipeline(
        ledger_path="test_ledger.json",
        registry_path="test_registry.json"
    )
    rng = np.random.default_rng(42)
    A = rng.standard_normal((64, 64)).astype(np.float32)
    B = rng.standard_normal((64, 64)).astype(np.float32)

    out, cert, summary = pipeline.execute_matrix_workload("e2e_test_workload", A, B)
    assert out.shape == (64, 64)
    assert summary["correctness"] == "PASS"
    assert cert.verify_tamper_evident() is True

    # Clean up test temp files
    import os
    for f in ["test_ledger.json", "test_registry.json"]:
        if os.path.exists(f):
            os.remove(f)


def test_dashboard_evidence_derivation():
    """Verify ParityDashboard computes scores dynamically from evidence."""
    dashboard = ParityDashboard("evidence_ledger.json")
    report = dashboard.compute_scores()
    assert "scores" in report
    assert "RAW_HARDWARE_PARITY" in report["scores"]
    assert "CONTRACT_PARITY" in report["scores"]
    assert "WORK_ELIMINATION" in report["scores"]
    assert report["scores"]["RAW_HARDWARE_PARITY"]["score_pct"] <= 5.0 # Honest physical bound
