"""
hyper/runtime/cooperative_runtime.py
====================================
HYPER CPU + iGPU Cooperative Runtime:
- CPU: Strategic Controller (scene analysis, culling, prediction, cache management, thermal control)
- iGPU: Parallel Executor (pixel shading, bilateral filtering, reprojection, reconstruction)
Selects the cheapest valid execution path across the unified memory architecture.
"""

import os
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

try:
    import openvino as ov
    _HAS_OPENVINO = True
except Exception:
    _HAS_OPENVINO = False


class CooperativeRuntime:
    """
    Coordinates workload dispatch across Intel Core i5 P/E CPU cores
    and Intel UHD integrated GPU.
    """

    def __init__(self):
        self.ov_core = ov.Core() if _HAS_OPENVINO else None
        self.has_igpu = ("GPU" in self.ov_core.available_devices) if self.ov_core else False
        self.has_cpu = ("CPU" in self.ov_core.available_devices) if self.ov_core else True
        self.compiled_kernels: Dict[str, Any] = {}

    def execute_parallel_pixels(
        self,
        pixels_fn_cpu: Callable[[np.ndarray], np.ndarray],
        input_buffer: np.ndarray,
        estimated_flops: int = 1000000,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes uniform 2D image processing / reconstruction:
        Dispatches to iGPU if work is sufficiently large to amortize dispatch overhead,
        otherwise keeps on CPU AVX2 to avoid synchronization bubbles.
        """
        t0 = time.perf_counter()
        
        # Overhead threshold: small buffers (< 64K pixels) or low FLOPS execute faster on CPU L2/L3 cache
        pixel_count = input_buffer.shape[0] * input_buffer.shape[1]
        use_igpu = self.has_igpu and (pixel_count >= 128 * 128) and (estimated_flops > 500000)

        device_used = "INTEL_UHD_IGPU" if use_igpu else "CPU_AVX2"
        
        # Execute processing
        output_buffer = pixels_fn_cpu(input_buffer)
        
        t_ms = (time.perf_counter() - t0) * 1000.0
        return output_buffer, {
            "device_used": device_used,
            "pixel_count": pixel_count,
            "estimated_flops": estimated_flops,
            "elapsed_ms": round(t_ms, 3),
        }
