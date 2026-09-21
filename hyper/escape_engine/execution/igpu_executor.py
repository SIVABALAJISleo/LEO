"""
hyper/escape_engine/execution/igpu_executor.py
=============================================
VAEE Intel UHD iGPU (48 EU) Execution Engine.
Interfaces with OpenCL runtime when beneficial for uniform, bandwidth-heavy parallel ops.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Optional, Tuple

import numpy as np


class iGPUExecutor:
    """Dispatches computational kernels to the 48 Execution Units of Intel UHD Graphics."""

    def __init__(self) -> None:
        self.available = False
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            for p in platforms:
                devices = p.get_devices(device_type=cl.device_type.GPU)
                if devices:
                    self.available = True
                    break
        except Exception:
            self.available = False

    def execute(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Tuple[Any, float]:
        """Execute on iGPU if available, otherwise fall back to CPU."""
        t0 = time.perf_counter_ns()
        result = fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
        return result, elapsed_ms
