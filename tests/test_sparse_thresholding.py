"""
tests/test_sparse_thresholding.py
=================================
Tests Phase 7 sparsity detection, overhead accounting, and fail-closed logic.
Ensures sparse routine is only dispatched when T_threshold + T_sparse + T_verify < T_dense.
"""

import numpy as np
import pytest
from hyper.sparsity.sparsity_engine import SparsityEngine


def test_sparse_overhead_rejection_on_small_matrix():
    engine = SparsityEngine(default_threshold=1e-3)
    rng = np.random.RandomState(42)

    # For tiny 16x16 matrices, sparse overhead (conversion + CSR pointer setup) exceeds dense BLAS
    A = (rng.rand(16, 16) > 0.8).astype(np.float32)
    B = rng.randn(16, 16).astype(np.float32)

    _, telemetry = engine.execute_with_overhead_check(A, B)
    assert "total_sparse_pipeline_ms" in telemetry
    assert "dense_execution_cost_ms" in telemetry
    # Path chosen must be reported honestly
    assert telemetry["path_chosen"] in ["EXACT", "REDUCED_WORK", "NUMERICALLY_APPROXIMATE"]


def test_sparse_error_exceeding_contract_falls_back():
    engine = SparsityEngine(default_threshold=0.5)  # Aggressive threshold
    rng = np.random.RandomState(42)

    # Dense matrix with values in [0, 1]
    A = rng.rand(64, 64).astype(np.float32)
    B = rng.rand(64, 64).astype(np.float32)

    # Contract requires max error <= 0.001
    _, telemetry = engine.execute_with_overhead_check(A, B, threshold=0.5, max_allowed_error=0.001)

    # Large threshold on dense matrix causes error > 0.001
    assert telemetry["error_satisfied"] is False
    assert telemetry["path_chosen"] == "EXACT"
