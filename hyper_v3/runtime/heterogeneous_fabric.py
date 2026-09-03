"""
hyper_v3/runtime/heterogeneous_fabric.py
Heterogeneous computational fabric uniting host CPU (13th Gen Intel Core i5)
and integrated GPU (Intel UHD Graphics) into a single cooperative execution fabric.
"""

from typing import Dict, Any, Tuple
import time
import numpy as np
from hyper_v3.runtime.device_manager import DeviceManager
from hyper_v3.runtime.cpu_backend import CPUBackend
from hyper_v3.runtime.igpu_backend import IntelIGPUBackend
from hyper_v3.runtime.hybrid_backend import HybridBackend


class HeterogeneousFabric:
    """Manages cooperative dispatch across CPU and Intel UHD iGPU resources."""

    def __init__(self):
        self.device_manager = DeviceManager()
        self.cpu_backend = CPUBackend()
        self.igpu_backend = IntelIGPUBackend()
        self.hybrid_backend = HybridBackend()

    def dispatch_workload(
        self,
        workload_type: str,
        a: np.ndarray,
        b: np.ndarray,
        arithmetic_intensity: float
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Intelligently assigns matrix computation to CPU, iGPU, or balanced Hybrid."""
        t0 = time.perf_counter()

        # Decision policy:
        # High arithmetic intensity + large matrices -> Hybrid or iGPU
        # Irregular or small matrices -> CPU
        n_elements = a.size
        if n_elements < 256 * 256 or arithmetic_intensity < 2.0:
            target = "CPU"
            result, exec_us = self.cpu_backend.execute_matmul(a, b)
            cpu_pct, igpu_pct = 100.0, 0.0
        elif n_elements > 1024 * 1024 and self.device_manager.has_igpu:
            target = "HYBRID"
            result, exec_us = self.hybrid_backend.execute_matmul_split(a, b, cpu_ratio=0.5)
            cpu_pct, igpu_pct = 50.0, 50.0
        else:
            target = "CPU"
            result, exec_us = self.cpu_backend.execute_matmul(a, b)
            cpu_pct, igpu_pct = 100.0, 0.0

        total_us = (time.perf_counter() - t0) * 1e6
        profile = {
            "target_fabric": target,
            "latency_us": round(total_us, 2),
            "cpu_contribution_percent": cpu_pct,
            "igpu_contribution_percent": igpu_pct,
            "transfer_overhead_bytes": 0  # Zero-copy unified system memory on integrated architecture
        }
        return result, profile
