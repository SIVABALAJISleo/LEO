"""
tests/test_hyper_v3_verifier.py
Unit tests for Independent Verifier, Freivalds algorithm, SSIM, Proof Engine, and Falsification.
"""

import pytest
import numpy as np
from hyper_v3.frontend.contract_parser import ContractParser
from hyper_v3.verification.independent_verifier import IndependentVerifier
from hyper_v3.proof.engine import ProofEngine
from hyper_v3.audit.falsification import FalsificationSuite


def test_independent_verifier_freivalds():
    a = np.random.randn(16, 16).astype(np.float32)
    b = np.random.randn(16, 16).astype(np.float32)
    c_correct = a @ b
    c_wrong = c_correct + 1.0

    assert IndependentVerifier.verify_freivalds_matmul(a, b, c_correct) is True
    assert IndependentVerifier.verify_freivalds_matmul(a, b, c_wrong) is False


def test_ssim_and_symplectic_drift():
    img1 = np.ones((32, 32))
    img2 = np.ones((32, 32))
    ssim = IndependentVerifier.compute_ssim_2d(img1, img2)
    assert ssim > 0.99

    pos1 = np.ones((10, 3))
    pos2 = np.ones((10, 3)) * 1.01
    assert IndependentVerifier.verify_symplectic_drift(pos1, pos2) is True


def test_proof_engine_and_falsification():
    contract = ContractParser.create_exact_contract("test_gemm")
    ref = np.ones((8, 8))
    cand = np.ones((8, 8))
    cert = ProofEngine.certify_transformation("exact_ref", "matmul", "matmul", ref, cand, contract)
    assert cert.verification_status == "PASS"

    assert FalsificationSuite.verify_no_self_certification() is True
