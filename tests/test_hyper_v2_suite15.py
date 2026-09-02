"""
tests/test_hyper_v2_suite15.py
Tests the 15-workload regression suite across Track A (Exact) and Track B (Contract-Aware).
"""

import pytest
from hyper_v2.compiler.contract_compiler import ExecutionTrack
from hyper_v2.workloads.suite_15 import WorkloadSuite15
from hyper_v2.audit.benchmark_runner import BenchmarkRunner
from hyper_v2.audit.holdout_runner import HoldoutRunner


def test_track_a_exact_suite():
    results = WorkloadSuite15.run_all_workloads(track=ExecutionTrack.TRACK_A_EXACT)
    assert len(results) == 15
    for r in results:
        assert r["track"] == "TRACK_A_EXACT"
        assert r["verified"] is True
        assert r["time_ms"] > 0.0


def test_track_b_contract_suite():
    results = WorkloadSuite15.run_all_workloads(track=ExecutionTrack.TRACK_B_CONTRACT)
    assert len(results) == 15
    passed_count = sum(1 for r in results if r["verified"])
    assert passed_count == 15  # 100% Contract Parity
    avg_avoidance = sum(r["work_avoided_pct"] for r in results) / 15
    assert avg_avoidance >= 90.0  # >90% verified computational work avoided


def test_benchmark_runner_full_audit():
    scoreboard = BenchmarkRunner.run_full_audit()
    assert scoreboard["summary"]["track_b_contract_parity"] == "15/15 (100.0%)"
    assert scoreboard["summary"]["fallback_rate_pct"] == 0.0


def test_holdout_runner_evaluation():
    holdout = HoldoutRunner.run_blind_holdout()
    assert holdout["compliance_rate_pct"] == 100.0
    assert holdout["overall_status"] == "PASS"
