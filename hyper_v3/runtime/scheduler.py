"""
hyper_v3/runtime/scheduler.py
Dynamic scheduler routing compute tasks to CPU, Intel iGPU, or Hybrid executors.
"""

from typing import Dict, Any, Tuple
import numpy as np
from hyper_v3.ir.operation import DeviceType
from hyper_v3.runtime.cpu_backend import CPUBackend
from hyper_v3.runtime.igpu_backend import IntelIGPUBackend
from hyper_v3.runtime.hybrid_backend import HybridBackend


class HeterogeneousScheduler:
    """Dispatches workloads to the optimal device target based on autotuner selection."""

    def __init__(self):
        self.cpu = CPUBackend()
        self.igpu = IntelIGPUBackend()
        self.hybrid = HybridBackend()

    def dispatch_matmul(self, a: np.ndarray, b: np.ndarray, target_device: DeviceType) -> Tuple[np.ndarray, float]:
        if target_device == DeviceType.IGPU and self.igpu.device_available:
            return self.igpu.execute_matmul(a, b)
        elif target_device == DeviceType.HYBRID and self.igpu.device_available:
            return self.hybrid.execute_matmul_split(a, b)
        return self.cpu.execute_matmul(a, b)
