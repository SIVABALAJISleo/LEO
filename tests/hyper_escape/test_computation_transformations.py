"""
tests/hyper_escape/test_computation_transformations.py
Validates Computation-Elimination Engine (Feature C / Section 5).
Tests mathematical transformations: FFT fast convolution, sparse matrix elimination,
operation count accounting, and work-elimination proof ledger.
"""
import pytest
import numpy as np

from hyper_universal.computation_elimination.engine import ComputationEliminationEngine


def test_fft_convolution_elimination():
    engine = ComputationEliminationEngine()

    # Signal length 2048, kernel length 128
    np.random.seed(42)
    signal = np.random.randn(2048).astype(np.float32)
    kernel = np.random.randn(128).astype(np.float32)

    # Reference direct spatial convolution
    ref_conv = np.convolve(signal, kernel, mode="same")

    # Fast FFT convolution
    fft_out, evidence = engine.fast_fft_convolution_1d(signal, kernel, mode="same")

    # Numerical equivalence: max error must be tiny
    assert np.allclose(fft_out, ref_conv, atol=1e-4, rtol=1e-4)

    # Validate work elimination ledger
    assert evidence.transformation_name == "FFT_FAST_CONVOLUTION"
    assert evidence.ops_before == 2 * len(signal) * len(kernel)
    assert evidence.ops_after < evidence.ops_before  # O(N log N) is significantly lower
    assert evidence.verified is True
    assert evidence.max_absolute_error < 1e-4


def test_sparse_execution_elimination():
    engine = ComputationEliminationEngine()

    # 1000 x 1000 matrix with 95% zeros
    np.random.seed(42)
    matrix = np.zeros((1000, 1000), dtype=np.float32)
    # populate 5% random nonzeros
    mask = np.random.rand(1000, 1000) < 0.05
    matrix[mask] = np.random.randn(np.sum(mask)).astype(np.float32)

    vec = np.random.randn(1000).astype(np.float32)
    ref_out = matrix @ vec

    # Sparse execution
    sparse_out, evidence = engine.sparse_matrix_vector_multiply(matrix, vec, sparsity_threshold=0.8)

    assert np.allclose(sparse_out, ref_out, atol=1e-5)
    assert evidence.transformation_name == "SPARSE_CSR_EXECUTION"
    assert evidence.ops_after < 0.10 * evidence.ops_before  # only non-zero entries processed
    assert evidence.verified is True


def test_sparse_execution_rejection_on_dense():
    engine = ComputationEliminationEngine()

    # Dense matrix with 0% zeros
    matrix = np.ones((100, 100), dtype=np.float32)
    vec = np.ones(100, dtype=np.float32)

    # Should raise ValueError because preconditions (sparsity >= 0.8) are violated
    with pytest.raises(ValueError, match="Precondition failed"):
        engine.sparse_matrix_vector_multiply(matrix, vec, sparsity_threshold=0.8)
