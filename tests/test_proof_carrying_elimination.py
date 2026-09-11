"""
tests/test_proof_carrying_elimination.py
========================================
Unit tests for Mechanism 1: Proof-Carrying Work Elimination.
Verifies machine-readable validity certificates, tamper resistance, and automatic fallback.
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass, CorrectnessTaxonomy
from hyper_cco.proof_elimination import (
    ProofCarryingEliminationEngine,
    RegionEliminationCertificate,
    ProofBundle,
    EliminationMode
)


def test_proof_bundle_validation():
    # Exact requires unchanged deps + deterministic + cache/oracle
    pb_exact = ProofBundle(
        dependencies_unchanged=True,
        operator_deterministic=True,
        cache_match=True,
        oracle_verified=True
    )
    assert pb_exact.is_valid_for_exact() is True

    pb_stale = ProofBundle(
        dependencies_unchanged=False,
        operator_deterministic=True,
        cache_match=True
    )
    assert pb_stale.is_valid_for_exact() is False


def test_certificate_seal_and_tamper_detection():
    contract = ComputeContract(
        workload_id="CERT_TEST",
        exactness_class=ExactnessClass.EXACT
    )
    engine = ProofCarryingEliminationEngine()

    A = np.ones((4, 4), dtype=np.float32)

    def proof_gen():
        return ProofBundle(
            dependencies_unchanged=True,
            operator_deterministic=True,
            cache_match=True,
            oracle_verified=True
        )

    out, cert = engine.execute_with_proof(
        region_id="layer_1",
        operator_identity="numpy.identity",
        operator_version="1.0",
        inputs=A,
        dependency_state={"state": 1},
        contract=contract,
        candidate_mode=EliminationMode.EXACT_REUSE,
        elimination_fn=lambda: A.copy(),
        exact_fallback_fn=lambda: A * 1.0,
        proof_generator=proof_gen,
        reason="Dependencies unchanged"
    )

    assert cert.mode == EliminationMode.EXACT_REUSE.value
    assert cert.verify_integrity() is True
    assert cert.verification_status == "PASS"

    # Tamper with certificate
    cert.error_bound = 999.0
    assert cert.verify_integrity() is False


def test_fallback_on_failed_proof():
    contract = ComputeContract(
        workload_id="FALLBACK_TEST",
        exactness_class=ExactnessClass.EXACT
    )
    engine = ProofCarryingEliminationEngine()

    def bad_proof_gen():
        # Missing dependencies_unchanged
        return ProofBundle(
            dependencies_unchanged=False,
            operator_deterministic=True,
            cache_match=False
        )

    fallback_called = False

    def exact_fallback():
        nonlocal fallback_called
        fallback_called = True
        return np.array([42.0])

    out, cert = engine.execute_with_proof(
        region_id="layer_fallback",
        operator_identity="test.op",
        operator_version="1.0",
        inputs=np.array([1.0]),
        dependency_state={},
        contract=contract,
        candidate_mode=EliminationMode.EXACT_REUSE,
        elimination_fn=lambda: np.array([0.0]),
        exact_fallback_fn=exact_fallback,
        proof_generator=bad_proof_gen
    )

    assert fallback_called is True
    assert out[0] == 42.0
    assert cert.mode == EliminationMode.FALLBACK.value
    assert cert.verify_integrity() is True
