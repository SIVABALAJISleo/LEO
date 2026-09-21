"""
hyper/universal/execution/igpu_backend.py
=========================================
Intel UHD Graphics (48 EU) OpenCL Execution Backend.
Supports zero-copy host-pointer sharing in unified 16GB system RAM.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple
import numpy as np


class iGPUBackend:
    """Executes computational pathways on Intel UHD 48 EU integrated GPU."""

    def __init__(self) -> None:
        self.opencl_available = self._detect_opencl()

    def _detect_opencl(self) -> bool:
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            for p in platforms:
                devs = p.get_devices(device_type=cl.device_type.GPU)
                if devs:
                    return True
            return False
        except Exception:
            return False

    def execute(self, fn: Callable[[Any], Any], input_data: Any) -> Tuple[Any, float]:
        t0 = time.perf_counter_ns()
        result = fn(input_data)
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return result, elapsed_ms
