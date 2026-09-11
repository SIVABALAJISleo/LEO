"""
tests/test_thermal_deadline_scheduler.py
========================================
Unit tests for Mechanism 6: Thermal-Aware Deadline Scheduling.
"""

import pytest
from hyper_cco.thermal_scheduler import (
    ThermalDeadlineScheduler,
    ScheduledTarget,
    CostWeights
)


def test_telemetry_sampling():
    scheduler = ThermalDeadlineScheduler()
    telem = scheduler.sample_telemetry()
    assert telem.cpu_utilization_pct >= 0.0
    assert telem.temperature_c > 0.0
    assert telem.package_power_w > 0.0


def test_scheduler_prefers_cpu_on_low_flops_high_transfer():
    scheduler = ThermalDeadlineScheduler()
    # Small kernel: 1e5 flops, 1MB data -> transfer overhead negates iGPU
    outcome = scheduler.schedule(
        kernel_name="small_vector_add",
        input_bytes=1024 * 1024,
        flop_count=1e5,
        deadline_ms=10.0,
        error_tolerance=1e-4
    )
    assert outcome.target == ScheduledTarget.CPU
    assert outcome.cost_J > 0.0


def test_scheduler_prefers_igpu_on_massive_compute():
    scheduler = ThermalDeadlineScheduler()
    # Heavy kernel: 5e9 flops, small 512KB input -> iGPU parallel throughput wins
    outcome = scheduler.schedule(
        kernel_name="massive_gemm",
        input_bytes=512 * 1024,
        flop_count=5e9,
        deadline_ms=50.0,
        error_tolerance=1e-3
    )
    assert outcome.target in (ScheduledTarget.INTEL_IGPU, ScheduledTarget.CPU_IGPU_PIPELINE)
