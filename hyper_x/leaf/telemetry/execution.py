"""
hyper_x/leaf/telemetry/execution.py
===================================
High-resolution execution telemetry reporting kernel and end-to-end latencies.

Rule (Phase 11):
    NEVER claim "microseconds" without measuring:
    - kernel execution
    - host-device / shared-memory operations
    - dispatch
    - synchronization
    - allocation
    - verification
    Report kernel latency AND end-to-end latency separately.
"""

from dataclasses import dataclass
import time
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ExecutionLatencyBreakdown:
    kernel_latency_us: float
    dispatch_overhead_us: float
    synchronization_us: float
    verification_overhead_us: float
    total_end_to_end_us: float

    @property
    def kernel_latency_ms(self) -> float:
        return self.kernel_latency_us / 1000.0

    @property
    def total_end_to_end_ms(self) -> float:
        return self.total_end_to_end_us / 1000.0


class ExecutionTimer:
    """Instruments execution with nanosecond precision."""

    def measure_phase(self, fn: Callable[[], Any]) -> Tuple[Any, float]:
        t0 = time.perf_counter_ns()
        res = fn()
        t1 = time.perf_counter_ns()
        return res, (t1 - t0) / 1000.0  # microseconds
