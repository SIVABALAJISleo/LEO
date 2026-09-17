"""
tests/v8/test_v8_residual.py
============================
Tests for ExactResidualEngine and mathematical residual correctness.
"""

import numpy as np
import pytest

from hyper.v8.contract import PathClassification
from hyper.v8.residual import ExactResidualEngine


def test_residual_first_call_is_fresh():
    engine = ExactResidualEngine()
    A = np.random.randn(10, 10).astype(np.float32)
    B = np.random.randn(10, 10).astype(np.float32)

    C, proof = engine.compute(A, B)
    ref = A @ B

    assert proof.path_type == PathClassification.EXACT_FRESH
    assert np.allclose(C, ref, atol=1e-5)


def test_residual_identical_call_is_identity():
    engine = ExactResidualEngine()
    A = np.random.randn(10, 10).astype(np.float32)
    B = np.random.randn(10, 10).astype(np.float32)

    C1, _ = engine.compute(A, B)
    C2, proof = engine.compute(A, B)

    assert proof.path_type == PathClassification.EXACT_REUSED
    assert proof.fraction_computed == 0.0
    assert np.array_equal(C1, C2)


def test_residual_row_sparse_delta():
    engine = ExactResidualEngine()
    A = np.random.randn(20, 20).astype(np.float32)
    B = np.random.randn(20, 20).astype(np.float32)

    # Initial compute
    engine.compute(A, B)

    # Modify 2 rows in A (10% perturbation)
    A_mod = A.copy()
    A_mod[0, :] += 0.5
    A_mod[5, :] -= 0.3

    C_res, proof = engine.compute(A_mod, B)
    ref = A_mod @ B

    assert proof.path_type == PathClassification.EXACT_RESIDUAL
    assert proof.fraction_computed < 1.0
    assert np.allclose(C_res, ref, atol=1e-5)


def test_residual_col_sparse_delta():
    engine = ExactResidualEngine()
    A = np.random.randn(20, 20).astype(np.float32)
    B = np.random.randn(20, 20).astype(np.float32)

    # Initial compute
    engine.compute(A, B)

    # Modify 1 column in B
    B_mod = B.copy()
    B_mod[:, 2] += 1.0

    C_res, proof = engine.compute(A, B_mod)
    ref = A @ B_mod

    assert proof.path_type == PathClassification.EXACT_RESIDUAL
    assert proof.fraction_computed < 1.0
    assert np.allclose(C_res, ref, atol=1e-5)
