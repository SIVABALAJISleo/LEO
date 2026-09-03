"""
hyper_v3/runtime/hybrid_backend.py
Heterogeneous CPU+iGPU dynamic partitioner and concurrent asynchronous executor.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from hyper_v3.runtime.cpu_backend import CPUBackend
from hyper_v3.runtime.igpu_backend import IntelIGPUBackend


class HybridBackend:
    """Dynamically partitions large matrix and signal workloads across CPU and Intel iGPU."""

    def __init__(self):
        self.cpu = CPUBackend()
        self.igpu = IntelIGPUBackend()

    def execute_matmul_split(self, a: np.ndarray, b: np.ndarray, cpu_ratio: float = 0.4) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        m = a.shape[0]
        split_point = int(m * cpu_ratio)

        a_cpu = a[:split_point, :]
        a_gpu = a[split_point:, :]

        c_cpu, _ = self.cpu.execute_matmul(a_cpu, b)
        c_gpu, _ = self.igpu.execute_matmul(a_gpu, b)

        c = np.vstack([c_cpu, c_gpu])
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return c, elapsed_us
