"""
hyper/escape_engine/analysis/cost_model.py
=========================================
VAEE Section 13: Empirical & Theoretical Cost Model.

Strictly distinguishes:
- THEORETICAL_COST (asymptotic FLOPs, theoretical memory traffic)
- MEASURED_COST (actual wall-clock monotonic time, peak RSS memory, CPU core utilization)
"""

from __future__ import annotations

import dataclasses
import os
import time
from typing import Any, Dict, Optional

import numpy as np


@dataclasses.dataclass
class MeasuredCost:
    wall_clock_ms: float
    cpu_time_ms: float
    peak_memory_mb: float
    data_movement_bytes: int
    energy_estimate_mj: float         # Millijoules estimate based on 45W TDP package
    cost_type: str = "MEASURED_COST"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class TheoreticalCost:
    asymptotic_complexity: str        # e.g., "O(N^3)", "O(N^2.807)", "O(N log N)"
    estimated_flops: int
    estimated_memory_bytes: int
    arithmetic_intensity: float       # FLOP / byte
    cost_type: str = "THEORETICAL_COST"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CostAnalyzer:
    """Analyzes and records theoretical vs measured hardware execution cost."""

    @staticmethod
    def measure_execution(
        fn: Any,
        *args: Any,
        trials: int = 3,
        package_power_w: float = 35.0, # Typical i5-12450H sustained power
    ) -> Tuple[Any, MeasuredCost]:
        """Runs function, measures timing and memory, and computes energy estimate."""
        import psutil
        proc = psutil.Process(os.getpid())

        # Warmup trial
        res = fn(*args)

        timings = []
        cpu_timings = []
        mem_before = proc.memory_info().rss

        for _ in range(trials):
            t_wall0 = time.perf_counter_ns()
            t_cpu0 = time.process_time_ns()
            res = fn(*args)
            t_wall1 = time.perf_counter_ns()
            t_cpu1 = time.process_time_ns()

            timings.append((t_wall1 - t_wall0) / 1e6)
            cpu_timings.append((t_cpu1 - t_cpu0) / 1e6)

        mem_after = proc.memory_info().rss
        peak_mb = max(0.01, (mem_after - mem_before) / (1024 * 1024))
        median_ms = float(np.median(timings))
        cpu_median_ms = float(np.median(cpu_timings))

        # Energy = Power (W) * Time (s) = Joules -> * 1000 = mJ
        energy_mj = (package_power_w * (median_ms / 1000.0)) * 1000.0

        # Estimate data movement
        data_bytes = 0
        for arg in args:
            if hasattr(arg, "nbytes"):
                data_bytes += arg.nbytes
        if hasattr(res, "nbytes"):
            data_bytes += res.nbytes

        cost = MeasuredCost(
            wall_clock_ms=round(median_ms, 4),
            cpu_time_ms=round(cpu_median_ms, 4),
            peak_memory_mb=round(peak_mb, 3),
            data_movement_bytes=data_bytes,
            energy_estimate_mj=round(energy_mj, 3),
        )
        return res, cost
