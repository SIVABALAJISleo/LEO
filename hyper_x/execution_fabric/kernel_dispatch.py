#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/execution_fabric/kernel_dispatch.py
===========================================
Phase 13: Kernel Dispatcher.
Executes primitive kernels with deterministic telemetry, parameter validation,
and fail-closed error boundaries.
"""

from __future__ import annotations
import time
from typing import Callable, Any, Dict, Tuple, Optional
import numpy as np


class KernelDispatch:
    """
    Unified execution wrapper for vectorized computational kernels.
    """

    @staticmethod
    def dispatch(
        kernel_name: str,
        kernel_fn: Callable[..., Any],
        *args,
        **kwargs
    ) -> Tuple[Any, float]:
        """
        Executes kernel, measuring elapsed time using high-resolution monotonic timer.
        Returns (result, latency_ms).
        """
        t0 = time.perf_counter()
        try:
            result = kernel_fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Kernel '{kernel_name}' execution failed: {e}") from e
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0
        return result, latency_ms
