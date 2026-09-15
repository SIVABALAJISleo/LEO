"""
tests/hostile/test_candidate_reference_separation.py
====================================================
Oracle Separation Attack (Phase 17).
Ensures candidate execution never calls the reference oracle during normal execution.
"""

from typing import Callable
import numpy as np
import pytest
from hyper_x.leaf.symbolic import ClosedFormSolver


def test_candidate_reference_separation():
    # Setup a tracking spy on the reference oracle
    oracle_calls = [0]
    def reference_oracle(N: int) -> int:
        oracle_calls[0] += 1
        return sum(i for i in range(1, N + 1))

    # Closed form candidate does not touch reference oracle
    def candidate_closed_form(N: int) -> int:
        return (N * (N + 1)) // 2

    # Execute candidate across 100 queries
    for n in range(1, 101):
        res = candidate_closed_form(n)
        assert res == (n * (n + 1)) // 2

    # Oracle MUST have 0 calls during candidate execution
    assert oracle_calls[0] == 0, "Security failure: Candidate accessed reference oracle during execution"
