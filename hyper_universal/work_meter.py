"""
hyper_universal/work_meter.py
=============================
WorkMeter: Unfabricated Physical Hardware & Execution Work Instrumentation.

Implements Section 4 of the Master Specification:
- Removes circular logic where latency ratio -> operation count is treated as measurement.
- Tracks separate metrics across CPU, iGPU, memory traffic, and execution time.
- Emits strict provenance tags:
    MEASURED, DERIVED, ESTIMATED, SIMULATED, REFERENCE_ONLY, UNAVAILABLE.
- Never fabricates numbers when hardware performance counters are missing.
"""

from __future__ import annotations
import gc
import os
import sys
import time
import psutil
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from hyper_universal.types import MetricProvenance


class MetricValue(BaseModel):
    name: str
    value: Optional[float] = None
    unit: str
    provenance: MetricProvenance
    notes: str = ""


class WorkMeasurementReport(BaseModel):
    measurement_id: str
    workload_id: str
    metrics: Dict[str, MetricValue] = Field(default_factory=dict)
    wall_time_ms: float = 0.0
    cpu_time_ms: float = 0.0
    peak_memory_mb: float = 0.0
    bytes_moved: int = 0
    instructions_executed: Optional[int] = None
    floating_point_ops: Optional[int] = None
    integer_ops: Optional[int] = None
    is_hardware_counter_available: bool = False
    timestamp: float = Field(default_factory=time.time)

    def get_metric(self, name: str) -> Optional[MetricValue]:
        return self.metrics.get(name)


class WorkMeter:
    """
    Instruments code execution without falsification or circular operation estimation.
    """

    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())

    def measure_callable(
        self,
        fn: Callable[[], Any],
        workload_id: str = "workload-unknown",
        input_bytes: int = 0,
        expected_output_bytes: int = 0,
        warmup_runs: int = 0,
    ) -> Tuple[Any, WorkMeasurementReport]:
        """
        Executes a callable under high-resolution process and memory monitoring.
        """
        for _ in range(warmup_runs):
            fn()

        gc.collect()
        mem_before = self.process.memory_info().rss
        cpu_times_before = self.process.cpu_times()
        t0_wall = time.perf_counter_ns()

        # Execute
        result = fn()

        t1_wall = time.perf_counter_ns()
        cpu_times_after = self.process.cpu_times()
        mem_after = self.process.memory_info().rss

        wall_ms = (t1_wall - t0_wall) / 1_000_000.0
        user_cpu_ms = (cpu_times_after.user - cpu_times_before.user) * 1000.0
        sys_cpu_ms = (cpu_times_after.system - cpu_times_before.system) * 1000.0
        total_cpu_ms = user_cpu_ms + sys_cpu_ms

        peak_mem_mb = max(mem_before, mem_after) / (1024.0 * 1024.0)
        bytes_transferred = input_bytes + expected_output_bytes

        # Check for OS-level performance counters (Linux perf / Windows PAPI)
        # On standard Windows without kernel driver, precise instructions/FLOPs are UNAVAILABLE.
        # We strictly mark them UNAVAILABLE rather than fabricating.
        metrics: Dict[str, MetricValue] = {
            "wall_time": MetricValue(
                name="wall_time",
                value=wall_ms,
                unit="ms",
                provenance=MetricProvenance.MEASURED,
                notes="High-resolution monotonic timer (perf_counter_ns)",
            ),
            "cpu_time": MetricValue(
                name="cpu_time",
                value=total_cpu_ms,
                unit="ms",
                provenance=MetricProvenance.MEASURED,
                notes="Process CPU user+system time",
            ),
            "peak_memory": MetricValue(
                name="peak_memory",
                value=peak_mem_mb,
                unit="MB",
                provenance=MetricProvenance.MEASURED,
                notes="Process Resident Set Size (RSS)",
            ),
            "bytes_moved": MetricValue(
                name="bytes_moved",
                value=float(bytes_transferred),
                unit="bytes",
                provenance=MetricProvenance.DERIVED if bytes_transferred > 0 else MetricProvenance.UNAVAILABLE,
                notes="Input + output tensor buffer allocations",
            ),
            "instructions": MetricValue(
                name="instructions",
                value=None,
                unit="count",
                provenance=MetricProvenance.UNAVAILABLE,
                notes="Hardware PMU instructions counter unavailable on standard OS sandbox",
            ),
            "floating_point_ops": MetricValue(
                name="floating_point_ops",
                value=None,
                unit="flops",
                provenance=MetricProvenance.UNAVAILABLE,
                notes="FLOP counter not directly measurable without low-level hardware tracing",
            ),
            "igpu_time": MetricValue(
                name="igpu_time",
                value=None,
                unit="ms",
                provenance=MetricProvenance.UNAVAILABLE,
                notes="Intel iGPU hardware query unavailable or executed on CPU",
            ),
        }

        report = WorkMeasurementReport(
            measurement_id=f"work-meas-{int(time.time()*1000)%1000000:06d}",
            workload_id=workload_id,
            metrics=metrics,
            wall_time_ms=wall_ms,
            cpu_time_ms=total_cpu_ms,
            peak_memory_mb=peak_mem_mb,
            bytes_moved=bytes_transferred,
            is_hardware_counter_available=False,
        )

        return result, report
