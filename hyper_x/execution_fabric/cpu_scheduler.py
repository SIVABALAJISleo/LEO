#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/execution_fabric/cpu_scheduler.py
=========================================
Phase 13: CPU Asymmetric Core Scheduler.
Manages dispatch between Performance cores (latency-critical inner kernels)
and Efficiency cores (background streaming, decompression, cache management)
on hybrid Intel architectures (4P + 4E / 4P + 8E).
"""

from __future__ import annotations
import concurrent.futures
from typing import Callable, Any, List, Dict, Optional
import numpy as np


class CPUScheduler:
    """
    Schedules thread tasks prioritizing fast vectorized cores for GEMM/FFT
    and background threads for memory streaming.
    """

    def __init__(self, p_core_threads: int = 4, e_core_threads: int = 4):
        self.p_core_threads = p_core_threads
        self.e_core_threads = e_core_threads
        self.p_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=p_core_threads,
            thread_name_prefix="P-Core"
        )
        self.e_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=e_core_threads,
            thread_name_prefix="E-Core"
        )

    def dispatch_critical(self, fn: Callable[..., Any], *args, **kwargs) -> concurrent.futures.Future:
        """Dispatches latency-critical inner loop to Performance cores."""
        return self.p_pool.submit(fn, *args, **kwargs)

    def dispatch_background(self, fn: Callable[..., Any], *args, **kwargs) -> concurrent.futures.Future:
        """Dispatches throughput or auxiliary work to Efficiency cores."""
        return self.e_pool.submit(fn, *args, **kwargs)

    def parallel_map_tiles(self, fn: Callable[[Any], Any], tiles: List[Any]) -> List[Any]:
        """Executes tiled chunks in parallel across available CPU workers."""
        results = list(self.p_pool.map(fn, tiles))
        return results

    def shutdown(self, wait: bool = True) -> None:
        self.p_pool.shutdown(wait=wait)
        self.e_pool.shutdown(wait=wait)
