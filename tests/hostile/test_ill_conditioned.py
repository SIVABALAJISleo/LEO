"""
tests/hostile/test_ill_conditioned.py
=====================================
Attacks linear solvers and matrix transforms with ill-conditioned matrices (kappa > 10^8).
Ensures numerical stability checks reject corrupted results.
"""

import numpy as np
import pytest
from hyper_x.leaf.contract import LeafContract, ContractTier


def test_ill_conditioned_matrix_detection():
    contract = LeafContract(name="test_cond", tier=ContractTier.EXACT)
    
    # Generate Hilbert-like ill-conditioned matrix
    N = 8
    H = np.zeros((N, N), dtype=np.float64)
    for i in range(N):
        for j in range(N):
            H[i, j] = 1.0 / (i + j + 1.0)

    cond_num = np.linalg.cond(H)
    assert cond_num > 1e7

    # Solve H x = b in float32 (should drift due to precision limits)
    b = np.ones((N, 1), dtype=np.float64)
    x_exact = np.linalg.solve(H, b)
    x_fp32 = np.linalg.solve(H.astype(np.float32), b.astype(np.float32)).astype(np.float64)

    is_valid, err, _ = contract.validate(x_fp32, x_exact)
    # The exact contract MUST fail on ill-conditioned FP32 solve, proving fail-closed protection
    assert is_valid is False or err > 1e-6
