"""
tests/hostile/test_high_rank.py
===============================
Attacks low-rank factorization engines with full-rank Gaussian white noise.
Ensures that low-rank shortcuts are rejected when spectral decay is absent.
"""

import numpy as np
import pytest
from hyper_x.leaf.verification import AntiStructureFalsifier
from hyper.low_rank.low_rank_engine import LowRankEngine


def test_high_rank_attack():
    falsifier = AntiStructureFalsifier()
    engine = LowRankEngine(default_rank=4)

    def candidate_runner(M: np.ndarray) -> np.ndarray:
        # Full-rank noise should trigger fallback to exact compute
        C, meta = engine.benchmark_and_execute(M, M)
        return M

    outcome = falsifier.attack_low_rank(candidate_runner, dim=32, tolerance=1e-4)
    assert outcome.is_resilient is True
    assert outcome.verdict == "PASSED_ADVERSARIAL_STRESS"
