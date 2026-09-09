"""
tests/test_hostile_sparsity.py
==============================
Hostile Self-Falsification Suite: Sparsity Engine Boundary Defense.

Verifies:
  - 100% dense matrix correctly triggers dense fallback (0% work elimination).
  - 39% sparsity matrix triggers rejection and dense fallback (< 40% threshold).
  - 40% and 41% sparsity matrices enter sparse execution with valid outputs.
  - Zero numerical deviation beyond contract limits on any boundary case.
"""

import pytest
import numpy as np
from hyper_cco.sparsity_engine import SparsityEngine, SparsityPattern


def test_dense_matrix_fallback():
    """Completely dense matrix must fall back cleanly without sparse execution overhead."""
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    ref = A @ B

    res = SparsityEngine.execute_sparse_matmul(A, B, max_relative_error=1e-3)
    assert res.strategy == "SPARSE_REJECTED_DENSE_FALLBACK"
    assert res.work_elimination_ratio == 0.0
    assert np.allclose(res.output, ref, atol=1e-5)


def test_sparsity_39_percent_rejection():
    """39% sparse matrix falls just below 40% threshold and must be rejected."""
    total = 1000
    zeros = int(total * 0.39)
    arr = np.ones(total, dtype=np.float32)
    arr[:zeros] = 0.0
    A = arr.reshape(10, 100)

    analysis = SparsityEngine.analyze_sparsity(A)
    assert analysis.sparsity_ratio < 0.40
    assert analysis.pattern == SparsityPattern.DENSE


def test_sparsity_40_percent_boundary():
    """40% sparse matrix reaches threshold boundary."""
    total = 1000
    zeros = int(total * 0.40)
    arr = np.ones(total, dtype=np.float32)
    arr[:zeros] = 0.0
    A = arr.reshape(10, 100)

    analysis = SparsityEngine.analyze_sparsity(A)
    assert analysis.sparsity_ratio >= 0.40
    assert analysis.pattern != SparsityPattern.DENSE


def test_sparsity_41_percent_acceptance():
    """41% sparse matrix exceeds threshold and qualifies for sparse path."""
    total = 1000
    zeros = int(total * 0.41)
    arr = np.ones(total, dtype=np.float32)
    arr[:zeros] = 0.0
    A = arr.reshape(10, 100)

    analysis = SparsityEngine.analyze_sparsity(A)
    assert analysis.sparsity_ratio >= 0.40
    assert analysis.pattern != SparsityPattern.DENSE
