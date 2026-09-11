"""
tests/test_contract_compiler.py
===============================
Unit tests for Mechanism 4: Contract Compiler.
"""

import pytest
from hyper_cco.contract import ComputeContract, ExactnessClass
from hyper_cco.contract_compiler import (
    ContractCompiler,
    ExecutionStrategy,
    TargetHardware,
    CompiledPlan
)


def test_compiler_selects_cache_when_available():
    compiler = ContractCompiler()
    contract = ComputeContract(
        workload_id="COMPILER_CACHE_TEST",
        allow_reuse=True
    )
    profile = {
        "cache_hit_available": True,
        "total_flops": 1e7
    }
    plan = compiler.compile(contract, profile)
    assert plan.strategy == ExecutionStrategy.CACHED_RESULT
    assert plan.estimated_cost_score < 0.1


def test_compiler_selects_sparse_on_high_sparsity():
    compiler = ContractCompiler()
    contract = ComputeContract(
        workload_id="COMPILER_SPARSE_TEST",
        allow_reduced_work=True
    )
    profile = {
        "cache_hit_available": False,
        "estimated_sparsity": 0.95,
        "total_flops": 1e6
    }
    plan = compiler.compile(contract, profile)
    assert plan.strategy == ExecutionStrategy.SPARSE_EXECUTION


def test_compiler_selects_igpu_for_large_parallel_kernel():
    compiler = ContractCompiler()
    contract = ComputeContract(
        workload_id="COMPILER_IGPU_TEST",
        max_latency_ms=100.0
    )
    profile = {
        "cache_hit_available": False,
        "total_flops": 5e8,  # > 1e8
        "igpu_available": True,
        "current_thermal_c": 60.0
    }
    plan = compiler.compile(contract, profile)
    assert plan.target_hardware == TargetHardware.INTEL_IGPU


def test_compiler_respects_thermal_limit():
    compiler = ContractCompiler()
    contract = ComputeContract(
        workload_id="COMPILER_THERMAL_TEST",
        custom_invariants={"thermal_limit_c": 70.0}
    )
    profile = {
        "cache_hit_available": False,
        "total_flops": 5e8,
        "igpu_available": True,
        "current_thermal_c": 82.0  # Above 70 C limit
    }
    plan = compiler.compile(contract, profile)
    # iGPU is throttled due to thermals, returns CPU exact
    assert plan.target_hardware == TargetHardware.CPU
