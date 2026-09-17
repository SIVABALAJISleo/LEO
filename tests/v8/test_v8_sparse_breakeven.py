"""
tests/v8/test_v8_sparse_breakeven.py
====================================
Tests for sparse representation break-even analysis.
"""

import numpy as np
import pytest
import scipy.sparse as sp


def test_sparse_accuracy_across_densities():
    N = 64
    rng = np.random.default_rng(42)

    for sparsity in [0.5, 0.8, 0.95, 0.99]:
        mask_A = rng.random((N, N)) > sparsity
        mask_B = rng.random((N, N)) > sparsity

        A = (rng.standard_normal((N, N)) * mask_A).astype(np.float32)
        B = (rng.standard_normal((N, N)) * mask_B).astype(np.float32)

        A_csr = sp.csr_matrix(A)
        B_csr = sp.csr_matrix(B)

        C_sparse = (A_csr @ B_csr).toarray()
        C_dense = A @ B

        assert np.allclose(C_sparse, C_dense, atol=1e-5)
