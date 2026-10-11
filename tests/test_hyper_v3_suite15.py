"""
tests/test_hyper_v3_suite15.py
Tests the 15-workload regression suite across Track A (Exact) and Track B (Contract-Aware).
"""

import pytest
from hyper_v3.frontend.contract_parser import ExecutionTrack
from hyper_v3.workloads.workload_registry import WORKLOAD_REGISTRY
from hyper_v3.frontend.contract_parser import ContractParser
from hyper_v3.benchmark.runner import BenchmarkRunner


def test_suite_15_workloads_run_without_errors():
    for name, fn in WORKLOAD_REGISTRY.items():
        exact_contract = ContractParser.create_exact_contract(name)
        contract_b = ContractParser.create_contract_aware_contract(name)

        out_a, time_a, ref_flops_a, act_flops_a = fn(exact_contract)
        out_b, time_b, ref_flops_b, act_flops_b = fn(contract_b)

        assert time_a > 0
        assert time_b > 0
        assert ref_flops_a > 0


def test_benchmark_runner_full_suite():
    runner = BenchmarkRunner()
    results = runner.run_all()
    assert len(results["workloads"]) == 15
    # Track A Exact: all 15 workloads pass bitwise/analytical parity
    assert results["summary"]["exact_parity_score"] == 1.0

    # Track B Contract-Aware: rigorously fails workloads that exceed declared tolerances
    assert results["workloads"]["dense_gemm_fp32"]["track_b_contract_aware"]["passed"] is False
    assert results["workloads"]["rasterization"]["track_b_contract_aware"]["passed"] is False
    assert results["workloads"]["bvh_hierarchy"]["track_b_contract_aware"]["passed"] is False
    assert results["workloads"]["fft_1d"]["track_b_contract_aware"]["passed"] is True
    assert results["workloads"]["vector_reduction"]["track_b_contract_aware"]["passed"] is True

    # Contract parity score reflects verified passing ratio (7/15 = 46.7%)
    assert results["summary"]["contract_parity_score"] == 7 / 15
    assert results["summary"]["mean_verified_work_avoidance"] > 0.5

