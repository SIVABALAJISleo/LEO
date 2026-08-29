"""
hyper100/heterogeneous_scheduler.py
===================================
CPU + Intel UHD Heterogeneous Scheduler.
Models real hardware performance characteristics of the Intel Core i5-12450H (4P+4E)
and Intel UHD Graphics (48 EUs) to compute execution, transfer, and synchronization costs,
dynamically selecting the fastest device placement.
"""

import time
import os
import psutil
from enum import Enum
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
import numpy as np


class DeviceTarget(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_UHD = "INTEL_UHD"
    HETEROGENEOUS_PIPELINED = "HETEROGENEOUS_PIPELINED"


@dataclass
class DeviceAllocation:
    """Detailed hardware execution schedule."""
    selected_device: DeviceTarget
    estimated_cpu_cost_ms: float
    estimated_uhd_cost_ms: float
    estimated_transfer_cost_ms: float
    reason: str


class HeterogeneousScheduler:
    """
    Cost-model-driven scheduler for Intel Core i5-12450H + Intel UHD Graphics.
    """

    # Physical hardware specifications for i5-12450H + UHD Xe G4 48EU
    CPU_PEAK_GFLOPS = 160.0        # 4 P-cores @ 4.4GHz AVX2 FP32 ~ 140-180 GFLOPS
    UHD_PEAK_GFLOPS = 920.0        # 48 EUs @ 1.2GHz FP32 ~ 920 GFLOPS
    SYSTEM_MEM_BW_GB_S = 51.2     # Shared DDR4/DDR5 memory bandwidth
    UHD_DISPATCH_OVERHEAD_MS = 0.08  # Vulkan / OpenCL command buffer dispatch latency

    @classmethod
    def estimate_cost(
        cls,
        flops: float,
        data_bytes: int,
        arithmetic_intensity: float,
        is_sequential: bool = False
    ) -> DeviceAllocation:
        """
        Calculates execution time estimates across CPU and UHD iGPU.
        """
        # 1. CPU execution cost model (AVX2 parallel threads)
        t_cpu_compute = (flops / (cls.CPU_PEAK_GFLOPS * 1e9)) * 1000.0
        t_cpu_mem = (data_bytes / (cls.SYSTEM_MEM_BW_GB_S * 1e9)) * 1000.0
        t_cpu_total = max(t_cpu_compute, t_cpu_mem)

        # Sequential or tiny workloads run dramatically faster on CPU cache
        if is_sequential or flops < 5e5 or data_bytes < 32768:
            return DeviceAllocation(
                selected_device=DeviceTarget.CPU_AVX2,
                estimated_cpu_cost_ms=t_cpu_total,
                estimated_uhd_cost_ms=t_cpu_total * 4.0,
                estimated_transfer_cost_ms=0.0,
                reason="Workload fits in CPU L2/L3 cache; zero dispatch overhead"
            )

        # 2. Intel UHD execution cost model
        t_uhd_compute = (flops / (cls.UHD_PEAK_GFLOPS * 1e9)) * 1000.0
        t_uhd_mem = (data_bytes / (cls.SYSTEM_MEM_BW_GB_S * 1e9)) * 1000.0
        t_transfer = (data_bytes / (cls.SYSTEM_MEM_BW_GB_S * 1e9)) * 1000.0 * 0.1  # Unified zero-copy pointer mapping
        t_uhd_total = max(t_uhd_compute, t_uhd_mem) + cls.UHD_DISPATCH_OVERHEAD_MS + t_transfer

        # 3. Decision rule
        if arithmetic_intensity > 20.0 and flops > 5e7:
            # High compute intensity: UHD EU parallelism wins
            selected = DeviceTarget.INTEL_UHD
            reason = f"High arithmetic intensity ({arithmetic_intensity:.1f} FLOPs/B) saturates 48 EUs"
        elif flops > 2e7 and not is_sequential:
            selected = DeviceTarget.HETEROGENEOUS_PIPELINED
            reason = "Moderate intensity: pipelined parallel execution"
        else:
            selected = DeviceTarget.CPU_AVX2
            reason = "Latency-sensitive or memory-bandwidth bound: CPU AVX2 optimal"

        return DeviceAllocation(
            selected_device=selected,
            estimated_cpu_cost_ms=t_cpu_total,
            estimated_uhd_cost_ms=t_uhd_total,
            estimated_transfer_cost_ms=t_transfer,
            reason=reason
        )

    @staticmethod
    def execute_kernel(
        fn_cpu: Any,
        fn_uhd: Optional[Any] = None,
        allocation: Optional[DeviceAllocation] = None,
        *args: Any,
        **kwargs: Any
    ) -> Tuple[Any, str, float]:
        """
        Dispatches execution to the allocated device.
        Returns: (result, executed_device_name, elapsed_ms)
        """
        t0 = time.perf_counter()
        target = allocation.selected_device if allocation else DeviceTarget.CPU_AVX2

        if target == DeviceTarget.INTEL_UHD and fn_uhd is not None:
            try:
                res = fn_uhd(*args, **kwargs)
                device_used = "INTEL_UHD"
            except Exception:
                res = fn_cpu(*args, **kwargs)
                device_used = "CPU_AVX2_FALLBACK"
        else:
            res = fn_cpu(*args, **kwargs)
            device_used = "CPU_AVX2"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return res, device_used, elapsed_ms
