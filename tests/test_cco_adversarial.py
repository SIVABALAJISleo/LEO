"""
tests/test_cco_adversarial.py
=============================
Adversarial Stress Battery & Scientific Self-Falsification Suite:
- Full-rank flat-spectrum matrix adversary (forces low-rank rejection and fallback)
- Dense non-zero matrix adversary (forces sparsity rejection and fallback)
- Ill-conditioned Hilbert matrix adversary
- Cache-busting input mutation adversary (ensures zero false cache hits)
- Proof that approximate results are NEVER returned when exact contract is requested
"""

import pytest
import numpy as np
from hyper_cco.optimizer import HyperCcoOptimizer
from hyper_cco.contract import ComputeContract, ExactnessClass, VerificationStatus
from hyper_cco.low_rank_engine import LowRankEngine
from hyper_cco.sparsity_engine import SparsityEngine


def test_adversarial_full_rank_matrix_rejects_low_rank():
    """
    Adversary: Random Gaussian matrix with flat singular value spectrum.
    Low-rank approximation MUST be rejected and fall back cleanly.
    """
    N = 64
    np.random.seed(999)
    A_full_rank = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)

    res = LowRankEngine.execute_low_rank_matmul(A_full_rank, B, rel_tolerance=1e-3)
    assert "FALLBACK" in res.strategy or "REJECTED" in res.strategy
    assert res.work_elimination_ratio == 0.0
    expected = A_full_rank @ B
    np.testing.assert_allclose(res.output, expected, rtol=1e-5, atol=1e-5)


def test_adversarial_dense_matrix_rejects_sparsity():
    """
    Adversary: Fully dense matrix with no zeros or near-zeros.
    Sparsity engine MUST reject sparse CSR and execute dense BLAS.
    """
    N = 64
    np.random.seed(888)
    A_dense = np.random.uniform(1.0, 5.0, size=(N, N)).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)

    res = SparsityEngine.execute_sparse_matmul(A_dense, B, max_relative_error=1e-3)
    assert "FALLBACK" in res.strategy or "REJECTED" in res.strategy
    assert res.work_elimination_ratio == 0.0
    expected = A_dense @ B
    np.testing.assert_allclose(res.output, expected, rtol=1e-5, atol=1e-5)


def test_adversarial_ill_conditioned_matrix_stability():
    """
    Adversary: Ill-conditioned Hilbert-style matrix (condition number > 1e8).
    Optimizer must maintain numerical stability without overflow/underflow or nan.
    """
    N = 16
    H = np.array([[1.0 / (i + j + 1.0) for j in range(N)] for i in range(N)], dtype=np.float32)
    B = np.random.randn(N, N).astype(np.float32)

    contract = ComputeContract(
        workload_id="HILBERT_ADVERSARIAL",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_relative_error=1e-3
    )
    optimizer = HyperCcoOptimizer()
    res = optimizer.execute_matrix_multiplication(H, B, contract=contract)

    assert not np.isnan(res.output).any()
    assert not np.isinf(res.output).any()
    expected = H @ B
    np.testing.assert_allclose(res.output, expected, rtol=1e-3, atol=1e-3)


def test_adversarial_cache_mutation_never_returns_stale_data():
    """
    Adversary: Subtly perturb input on consecutive executions.
    Full-content cache MUST detect the perturbation and never return stale cached output.
    """
    optimizer = HyperCcoOptimizer()
    N = 32
    A = np.ones((N, N), dtype=np.float32)
    B = np.ones((N, N), dtype=np.float32)

    contract = ComputeContract(workload_id="CACHE_MUTATION_TEST")

    # Run 1: All ones -> Output is N * ones
    res1 = optimizer.execute_matrix_multiplication(A, B, contract=contract)
    assert np.isclose(res1.output[0, 0], float(N), rtol=1e-4)

    # Run 2: Subtly modify single element in A
    A_perturbed = A.copy()
    A_perturbed[10, 10] = 50.0

    res2 = optimizer.execute_matrix_multiplication(A_perturbed, B, contract=contract)
    assert res2.cache_hit is False
    assert np.isclose(res2.output[10, 0], float(N - 1 + 50.0), rtol=1e-4)


def test_exact_contract_never_approximated():
    """
    Requirement 52: Adaptive contract relaxation must NEVER silently weaken exact contract.
    When EXACT contract is requested, low-rank or sparse approximations MUST NOT be used.
    """
    optimizer = HyperCcoOptimizer()
    N = 32
    A = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)

    strict_contract = ComputeContract(
        workload_id="STRICT_EXACT_WORKLOAD",
        exactness_class=ExactnessClass.EXACT,
        allow_approximation=False
    )
    res = optimizer.execute_matrix_multiplication(A, B, contract=strict_contract)
    assert res.exactness_class in (ExactnessClass.EXACT, ExactnessClass.EXACT_REFORMULATION, ExactnessClass.CACHED)
    assert res.measured_absolute_error == 0.0
