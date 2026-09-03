"""
tests/test_hyper_mvc_dar_verification.py
Unit tests for Independent Verifier: Freivalds algorithm, Metamorphic testing,
Hamiltonian energy drift, and Perceptual SSIM checks.
"""

import pytest
import numpy as np
from hyper_mvc_dar import IndependentVerifier


def test_freivalds_matrix_multiplication_verifier():
    np.random.seed(42)
    a = np.random.randn(64, 64).astype(np.float32)
    b = np.random.randn(64, 64).astype(np.float32)
    c_correct = a @ b

    assert IndependentVerifier.verify_matrix_multiply_freivalds(a, b, c_correct) is True

    # Corrupt one entry
    c_corrupted = c_correct.copy()
    c_corrupted[0, 0] += 5.0
    assert IndependentVerifier.verify_matrix_multiply_freivalds(a, b, c_corrupted) is False


def test_metamorphic_linearity_verifier():
    linear_op = lambda x: x * 3.5
    x = np.random.randn(32, 32)
    assert IndependentVerifier.verify_metamorphic_linearity(linear_op, x, alpha=2.0) is True

    non_linear_op = lambda x: x ** 2
    assert IndependentVerifier.verify_metamorphic_linearity(non_linear_op, x, alpha=2.0) is False


def test_hamiltonian_energy_conservation():
    h0 = 100.0
    h_stable = 100.005  # 0.005% drift
    assert IndependentVerifier.verify_hamiltonian_conservation(h0, h_stable, tolerance=1e-3) is True

    h_divergent = 105.0  # 5% drift
    assert IndependentVerifier.verify_hamiltonian_conservation(h0, h_divergent, tolerance=1e-3) is False


def test_ssim_perceptual_verifier():
    ref = np.random.uniform(0, 1, size=(64, 64))
    identical = ref.copy()
    passed, ssim_val = IndependentVerifier.verify_ssim_perceptual(ref, identical, threshold=0.95)
    assert passed is True
    assert ssim_val == pytest.approx(1.0, abs=1e-3)

    noisy = ref + np.random.normal(0, 0.5, size=(64, 64))
    passed_noisy, ssim_noisy = IndependentVerifier.verify_ssim_perceptual(ref, noisy, threshold=0.95)
    assert passed_noisy is False
    assert ssim_noisy < 0.95
