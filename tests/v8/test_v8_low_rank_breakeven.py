"""
tests/v8/test_v8_low_rank_breakeven.py
======================================
Tests for low-rank factorization and numerical stability.
"""

import numpy as np
import pytest


def test_factored_gemm_mathematical_identity():
    N = 64
    r = 4
    rng = np.random.default_rng(123)

    U = rng.standard_normal((N, r)).astype(np.float32)
    V = rng.standard_normal((r, N)).astype(np.float32)
    A = U @ V
    B = rng.standard_normal((N, N)).astype(np.float32)

    # Standard: A @ B
    C_standard = A @ B

    # Factored: U @ (V @ B)
    C_factored = U @ (V @ B)

    assert np.allclose(C_standard, C_factored, atol=1e-4)
