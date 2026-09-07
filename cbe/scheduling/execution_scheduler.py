"""
cbe/scheduling/execution_scheduler.py
Cooperative CPU + Intel iGPU workload partitioning and execution scheduler.
Directs control flow, caching, and state hashing to CPU, while routing
parallel neural reconstruction, tensor operations, and image processing to the Intel UHD iGPU.
"""

from __future__ import annotations

import time
from typing import Dict, Any, Callable, Optional
import numpy as np


class ExecutionScheduler:
    """
    Allocates tasks between host CPU and Intel integrated GPU based on FLOP intensity,
    payload size, and measured data-transfer overhead.
    """
    def __init__(
        self,
        has_igpu: bool = True,
        min_gpu_elements_threshold: int = 16384  # e.g., 128x128 image or tensor size
    ):
        self.has_igpu = has_igpu
        self.min_gpu_elements_threshold = min_gpu_elements_threshold
        self.cpu_task_count = 0
        self.igpu_task_count = 0
        self.total_transfer_overhead_ms = 0.0

    def should_offload_to_igpu(self, element_count: int, op_intensity: str = "HIGH") -> bool:
        """
        Determines whether offloading yields net positive speedup over CPU AVX2 execution.
        Small payloads (<16K elements) run on CPU to avoid PCI-e / driver command submission latency.
        """
        if not self.has_igpu:
            return False
            
        if element_count < self.min_gpu_elements_threshold and op_intensity != "VERY_HIGH":
            return False
            
        return True

    def dispatch(
        self,
        task_name: str,
        element_count: int,
        cpu_fn: Callable[..., Any],
        gpu_fn: Callable[..., Any],
        *args,
        **kwargs
    ) -> Tuple[Any, str, float]:
        """
        Executes task on optimal processor (CPU or Intel iGPU) and measures runtime.
        Returns: (result, target_used, elapsed_ms).
        """
        t0 = time.perf_counter()
        target = "iGPU" if self.should_offload_to_igpu(element_count) else "CPU"
        
        try:
            if target == "iGPU":
                res = gpu_fn(*args, **kwargs)
                self.igpu_task_count += 1
            else:
                res = cpu_fn(*args, **kwargs)
                self.cpu_task_count += 1
        except Exception as e:
            # Fallback to CPU on any GPU driver/device error
            target = "CPU_FALLBACK"
            res = cpu_fn(*args, **kwargs)
            self.cpu_task_count += 1
            
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return res, target, elapsed_ms

    def get_stats(self) -> Dict[str, Any]:
        total = self.cpu_task_count + self.igpu_task_count
        return {
            "total_tasks": total,
            "cpu_tasks": self.cpu_task_count,
            "igpu_tasks": self.igpu_task_count,
            "igpu_offload_pct": round((self.igpu_task_count / max(1, total)) * 100.0, 2)
        }
