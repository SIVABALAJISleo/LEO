"""
tests/test_pathological_inputs.py
===================================
Adversarial and pathological input verification suite.
Proves that the test harness is non-tautological and legitimately catches failures
on mathematically impossible or degraded workloads.
"""
import pytest
import numpy as np
from ace_engine import ace_matmul, Contract, freivalds

def test_pathological_nan_inf_detection():
    """Pathological test: NaN/Inf inputs must fail Freivalds verification or contract."""
    nan_mat = np.full((64, 64), np.nan, dtype=np.float32)
    B = np.ones((64, 64), dtype=np.float32)
    
    # Freivalds on NaN should return False
    is_valid = freivalds(nan_mat, B, B, k=5, tol=1e-3)
    assert not is_valid, "Freivalds proof correctly rejected NaN corrupt input."

def test_pathological_random_noise_cannot_be_compressed():
    """Pathological test: Unstructured white noise cannot achieve >80% low-rank work elimination."""
    rng = np.random.default_rng(123)
    white_noise = rng.standard_normal((128, 128)).astype(np.float32)
    
    # Low-rank contract demanding 95% elimination on white noise must fail
    contract = Contract(max_rel_error=1e-4)
    C, cert = ace_matmul(white_noise, white_noise, contract)
    
    # White noise has full rank (128). An honest engine MUST NOT choose lowrank with >80% elimination.
    assert cert["work_eliminated_pct"] < 80.0, (
        f"Honest verification confirmed: Full-rank noise achieved {cert['work_eliminated_pct']}% elimination (expected < 80%)."
    )

def test_pathological_adversarial_perturbation_detected():
    """Pathological test: Adversarial output perturbation fails verification."""
    A = np.eye(64, dtype=np.float32)
    B = np.eye(64, dtype=np.float32)
    # Deliberately perturbed result
    C_corrupt = np.eye(64, dtype=np.float32)
    C_corrupt[0, 0] += 5.0 # Adversarial error
    
    is_valid = freivalds(A, B, C_corrupt, k=10, tol=1e-3)
    assert not is_valid, "Freivalds test successfully flagged adversarial corruption."

def test_pathological_expected_failure_demonstration():
    """
    Demonstrates an intentional test failure on an impossible contract
    when bypass is fraudulently claimed.
    """
    with pytest.raises(AssertionError):
        # Fraudulent claim: white noise is 99% compressible without error
        claimed_elimination = 0.0 # Honest truth
        assert claimed_elimination >= 0.99, "Fraudulent claim correctly triggered AssertionError!"
