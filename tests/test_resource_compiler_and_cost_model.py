"""
tests/test_resource_compiler_and_cost_model.py
==============================================
Validation suite for Phase 9 (CPU/iGPU Resource Compiler) & Phase 10 (Total Cost Model).
"""

import numpy as np
import pytest

from hyper.research_engine.resource_compiler import (
    ExecutionDevice,
    HeterogeneousResourceCompiler,
    ResourcePlan,
    TotalCostBreakdown,
    TotalCostModel,
)


def test_total_cost_model_breakdown_and_amortization():
    def sample_workload(inputs):
        return inputs["A"] @ inputs["B"]

    inputs = {
        "A": np.random.randn(64, 64).astype(np.float32),
        "B": np.random.randn(64, 64).astype(np.float32),
    }

    # Simulate a pathway that had 50ms discovery, 10ms compilation, 15ms verification
    breakdown = TotalCostModel.measure(
        fn=sample_workload,
        sample_inputs=inputs,
        discovery_cost_ms=50.0,
        compilation_cost_ms=10.0,
        verification_cost_ms=15.0,
        data_movement_bytes=64 * 64 * 4 * 2,
    )

    assert isinstance(breakdown, TotalCostBreakdown)
    assert breakdown.discovery_cost_ms == 50.0
    assert breakdown.compilation_cost_ms == 10.0
    assert breakdown.verification_cost_ms == 15.0
    assert breakdown.execution_cost_ms > 0.0
    assert breakdown.data_movement_cost_ms > 0.0

    # Test One-Shot Cost
    one_shot = breakdown.one_shot_cost_ms
    assert one_shot > 75.0  # 50 + 10 + 15 + exec

    # Test Amortized Cost over N=1000 runs
    amortized_1000 = breakdown.amortized_cost_ms(1000)
    assert amortized_1000 < one_shot
    # One-time overhead per run is 75 / 1000 = 0.075ms
    assert amortized_1000 < (breakdown.execution_cost_ms + 1.0)

    # Telemetry presence
    d = breakdown.to_dict(n_executions=1000)
    assert "components_ms" in d
    assert "telemetry" in d
    assert d["telemetry"]["peak_ram_bytes"] > 0
    assert d["telemetry"]["power_watts"] >= 20.0


def test_heterogeneous_resource_compiler_routing():
    # Small payload -> CPU_ONLY
    plan_small = HeterogeneousResourceCompiler.compile_resource_plan(
        total_flops=1e5,
        input_bytes=1024 * 16,
        output_bytes=1024 * 16,
        is_fused_pipeline=False,
    )
    assert plan_small.selected_device in (ExecutionDevice.CPU_ONLY, ExecutionDevice.CPU_P_CORE)

    # Large high-intensity workload -> iGPU or Heterogeneous pipeline
    plan_large = HeterogeneousResourceCompiler.compile_resource_plan(
        total_flops=1e9,
        input_bytes=1024 * 1024 * 8,
        output_bytes=1024 * 1024 * 8,
        is_fused_pipeline=True,
    )
    assert plan_large.selected_device in (
        ExecutionDevice.CPU_PLUS_IGPU,
        ExecutionDevice.HETEROGENEOUS_PIPELINE,
        ExecutionDevice.IGPU_ONLY,
        ExecutionDevice.INTEL_IGPU,
    )
    assert plan_large.dram_traffic_eliminated_pct > 0.0
