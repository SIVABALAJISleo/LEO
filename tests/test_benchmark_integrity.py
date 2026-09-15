"""
tests/test_benchmark_integrity.py
=================================
Tests Phase 13 & 14 benchmark integrity and statistical consistency.
Verifies that timing percentiles satisfy mathematical invariants.
"""

import pytest
from hyper.benchmark.workload_suite import MasterWorkloadSuite, measure_execution_stats


def test_measure_execution_stats_invariants():
    # Simple workload
    val, stats = measure_execution_stats(lambda: sum(range(1000)), warmup_runs=5, measured_runs=15)
    assert val == 499500
    assert stats["min"] <= stats["median"]
    assert stats["median"] <= stats["max"]
    assert stats["min"] <= stats["p95"] <= stats["max"]
    assert stats["std_dev"] >= 0.0


def test_workload_suite_returns_measured_data():
    suite = MasterWorkloadSuite()
    res = suite.run_workload_1_dense_gemm(N=64, warmup=3, runs=10)

    assert "baseline_latency_ms" in res
    assert "candidate_latency_ms" in res
    assert "measured_speedup" in res
    assert "work_eliminated_pct" in res
    assert 0.0 <= res["work_eliminated_pct"] <= 100.0

    # Ensure speedup is calculated from measured medians
    expected_speedup = res["baseline_latency_ms"]["median"] / res["candidate_latency_ms"]["median"]
    assert abs(res["measured_speedup"] - expected_speedup) < 0.01
