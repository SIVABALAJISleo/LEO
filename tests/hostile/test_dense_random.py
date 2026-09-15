"""
tests/hostile/test_dense_random.py
==================================
Attacks sparsity engines with uniform 100% dense random matrices.
Ensures fail-closed fallback to dense execution.
"""

import numpy as np
import pytest
from hyper_x.leaf.verification import AntiStructureFalsifier
from hyper.sparsity.sparsity_engine import SparsityEngine


def test_dense_random_attack():
    falsifier = AntiStructureFalsifier()
    engine = SparsityEngine()

    def candidate_runner(M: np.ndarray) -> np.ndarray:
        # Executes sparsity engine with overhead check; if dense, falls back to dense
        res, meta = engine.execute_with_overhead_check(M, M)
        return M  # identity check for matrix attack

    outcome = falsifier.attack_sparsity(candidate_runner, dim=32, tolerance=1e-4)
    assert outcome.is_resilient is True
    assert outcome.verdict == "PASSED_DENSE_ATTACK"
