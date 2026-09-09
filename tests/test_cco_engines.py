"""
tests/test_cco_engines.py
=========================
Unit tests for Core Optimization Engines:
- Incremental delta computation
- Residual-first matrix execution
- Common subexpression elimination (CSE)
- Algebraic reformulations (Associative rechaining, Sherman-Morrison, FFT convolution)
- Adaptive low-rank randomized SVD
- Sparsity CSR execution
"""

import pytest
import numpy as np
from hyper_cco.incremental_engine import IncrementalEngine, DeltaType
from hyper_cco.residual_engine import ResidualEngine
from hyper_cco.cse_engine import CommonSubexpressionEngine, DagNode
from hyper_cco.algebraic_engine import AlgebraicReformulationEngine
from hyper_cco.low_rank_engine import LowRankEngine
from hyper_cco.sparsity_engine import SparsityEngine


def test_incremental_engine_sparse_column_update():
    A = np.random.randn(32, 32).astype(np.float32)
    B_prev = np.random.randn(32, 32).astype(np.float32)
    Y_prev = A @ B_prev

    # Perturb only column 5 of B
    B_curr = B_prev.copy()
    B_curr[:, 5] += 2.5

    res = IncrementalEngine.execute_incremental_matmul(A, B_curr, B_prev, Y_prev)
    assert res.delta_analysis.delta_type == DeltaType.SPARSE_CHANGE
    assert res.work_elimination_ratio > 0.80 # ~31 of 32 columns avoided
    # Numerical correctness
    expected = A @ B_curr
    np.testing.assert_allclose(res.output, expected, rtol=1e-4, atol=1e-4)


def test_residual_engine_low_rank_sparse_correction():
    # Construct rank-4 matrix with noise
    np.random.seed(42)
    U = np.random.randn(64, 4)
    V = np.random.randn(64, 4)
    A = (U @ V.T).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    res = ResidualEngine.execute_matrix_residual(A, B, rank_k=4, residual_tolerance=1e-3)
    assert res.work_elimination_ratio > 0.40
    expected = A @ B
    np.testing.assert_allclose(res.output, expected, rtol=1e-3, atol=1e-3)


def test_algebraic_associative_rechain_vector():
    M, K, N = 64, 64, 64
    A = np.random.randn(M, K).astype(np.float32)
    B = np.random.randn(K, N).astype(np.float32)
    v = np.random.randn(N, 1).astype(np.float32)

    out, record = AlgebraicReformulationEngine.associative_rechain_vector(A, B, v)
    expected = (A @ B) @ v
    assert record.is_exact is True
    assert record.operations_eliminated_ratio > 0.80
    np.testing.assert_allclose(out, expected, rtol=1e-4, atol=1e-4)


def test_algebraic_sherman_morrison():
    N = 32
    np.random.seed(42)
    A = np.random.randn(N, N).astype(np.float64) + np.eye(N) * 5.0 # well-conditioned
    A_inv = np.linalg.inv(A)
    u = np.random.randn(N).astype(np.float64)
    v = np.random.randn(N).astype(np.float64)
    b = np.random.randn(N).astype(np.float64)

    out, record = AlgebraicReformulationEngine.sherman_morrison_rank1_solve(A_inv, u, v, b)
    expected = np.linalg.solve(A + np.outer(u, v), b)
    assert record.is_exact is True
    assert record.operations_eliminated_ratio > 0.50
    np.testing.assert_allclose(out, expected, rtol=1e-5, atol=1e-5)


def test_algebraic_fft_convolution_1d():
    signal = np.sin(np.linspace(0, 10, 256)).astype(np.float32)
    kernel = np.array([0.2, 0.5, 0.2], dtype=np.float32)

    out, record = AlgebraicReformulationEngine.fft_convolution_1d(signal, kernel)
    expected = np.convolve(signal, kernel, mode="full")
    assert record.is_exact is True
    np.testing.assert_allclose(out, expected, rtol=1e-4, atol=1e-4)


def test_sparsity_engine_csr_execution():
    A = np.zeros((64, 64), dtype=np.float32)
    # 80% sparse
    np.random.seed(42)
    indices = np.random.choice(64 * 64, size=int(64 * 64 * 0.15), replace=False)
    A.ravel()[indices] = np.random.randn(len(indices))
    B = np.random.randn(64, 64).astype(np.float32)

    res = SparsityEngine.execute_sparse_matmul(A, B, max_relative_error=1e-3)
    assert "ACCELERATED" in res.strategy
    assert res.work_elimination_ratio > 0.70
    expected = A @ B
    np.testing.assert_allclose(res.output, expected, rtol=1e-4, atol=1e-4)


def test_cse_engine_deduplication():
    cse = CommonSubexpressionEngine()
    node_a = DagNode("node_a", "input_tensor", [], {"id": 1})
    node_b = DagNode("node_b", "input_tensor", [], {"id": 2})

    # Subexpression 1: A @ B
    matmul_1 = DagNode("m1", "matmul", [node_a, node_b])
    can_1, reused_1 = cse.register_or_reuse(matmul_1, op_cost=100.0)
    assert reused_1 is False

    # Subexpression 2: A @ B (duplicate)
    matmul_2 = DagNode("m2", "matmul", [node_a, node_b])
    can_2, reused_2 = cse.register_or_reuse(matmul_2, op_cost=100.0)
    assert reused_2 is True
    assert can_2 is can_1
    assert cse.eliminated_subexpressions == 1
    assert cse.saved_operations == 100.0
