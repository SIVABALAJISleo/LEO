"""
tests/test_hostile_low_rank.py
==============================
Hostile Self-Falsification Suite: Low-Rank Engine Flat-Spectrum Defense.

Verifies:
  - Random Gaussian matrix with flat singular value spectrum (sigma_decay >= 0.6)
    is detected and rejected to prevent catastrophic accuracy collapse.
  - Truly low-rank matrix (e.g. rank 2) is accepted and achieves verified work reduction.
"""

import pytest
import numpy as np
from hyper_cco.low_rank_engine import LowRankEngine


def test_flat_spectrum_gaussian_matrix_rejected():
    """Full-rank random Gaussian matrix has flat spectrum and must be rejected."""
    rng = np.random.RandomState(42)
    A = rng.randn(64, 64).astype(np.float32)
    B = rng.randn(64, 64).astype(np.float32)
    ref = A @ B

    res = LowRankEngine.execute_low_rank_gemm(A, B, max_rank=8, max_relative_error=1e-3)
    # Must reject low-rank and fall back to full BLAS
    assert "FALLBACK" in res.strategy
    assert res.work_elimination_ratio == 0.0
    assert np.allclose(res.output, ref, atol=1e-4)


def test_true_low_rank_matrix_accepted():
    """Rank-2 matrix has steep spectrum decay and should be compressed."""
    rng = np.random.RandomState(42)
    # Construct rank-2 matrix
    U = rng.randn(64, 2).astype(np.float32)
    V = rng.randn(2, 64).astype(np.float32)
    A_low_rank = U @ V
    B = rng.randn(64, 64).astype(np.float32)
    ref = A_low_rank @ B

    res = LowRankEngine.execute_low_rank_gemm(A_low_rank, B, max_rank=4, max_relative_error=1e-2)
    # Must accept low-rank and achieve work reduction
    assert "SVD" in res.strategy
    assert res.work_elimination_ratio > 0.50
    assert np.allclose(res.output, ref, atol=1e-2)
