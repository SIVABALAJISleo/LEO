"""
hyper_x/leaf/runtime/cpu.py
===========================
CPU execution backend for Intel Core i5-12450H with P-core affinity.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.extreme.affinity_scheduler import AlderLakeAffinityScheduler


class LeafCPURuntime:
    """CPU backend optimized for Alder Lake 4 P-cores / 12 threads with AVX2."""

    def __init__(self):
        self.scheduler = AlderLakeAffinityScheduler()

    def execute(self, fn: Callable[[], np.ndarray], pin_p_cores: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        if pin_p_cores:
            with self.scheduler.pin_p_cores():
                result = fn()
        else:
            result = fn()
        t1 = time.perf_counter_ns()

        elapsed_ms = (t1 - t0) / 1e6
        return result, {
            "backend": "INTEL_I5_12450H_CPU",
            "p_cores_pinned": pin_p_cores,
            "kernel_ms": elapsed_ms,
            "end_to_end_ms": elapsed_ms,
        }
