"""
tests/test_hyper_v3_adversarial.py
Tests the holdout and adversarial benchmark suites.
"""

import pytest
from hyper_v3.benchmark.holdout import HoldoutRunner


def test_holdout_runner():
    res = HoldoutRunner.run_all()
    assert "holdout_odd_gemm" in res
    assert "holdout_multiscale_fft" in res
    assert "adv_ill_conditioned_gemm" in res
    assert res["holdout_odd_gemm"]["status"] == "PASS"
