"""
tests/v8/test_v8_falsification.py
=================================
Tests for SelfFalsificationEngine and 12 adversarial test cases.
"""

import pytest

from hyper.v8.falsification import SelfFalsificationEngine


def test_falsification_all_cases():
    engine = SelfFalsificationEngine()
    results = engine.run_all(N=32)

    assert len(results) == 12
    # Every test must execute without uncaught exceptions and pass contract validation
    failed = [r.category for r in results if not r.passed]
    assert len(failed) == 0, f"Adversarial tests failed: {failed}"


def test_falsification_nan_handling():
    engine = SelfFalsificationEngine()
    res = engine._test_nan_inf(N=16)
    assert res.passed
