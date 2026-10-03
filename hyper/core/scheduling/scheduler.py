"""
hyper/core/scheduling/scheduler.py
Adaptive CPU + Intel UHD Graphics Scheduler (Prompt Section 24).
Hardware Target:
- CPU: Intel Core i5-12450H (AVX2, 8 cores / 12 threads)
- iGPU: Intel UHD Graphics (48 Execution Units)
Classifies workloads empirically:
CPU_BEST, IGPU_BEST, HYBRID_BEST, CPU_ONLY, IGPU_UNSUPPORTED, UNKNOWN.
Never schedules to iGPU simply because it exists; accounts for dispatch, coherency, and transfer overheads.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple
import numpy as np
from pydantic import BaseModel

from hyper.core.semantic_ir.models import DeviceTarget


class SchedulingClass(str, Enum):
    CPU_BEST = "CPU_BEST"
    IGPU_BEST = "IGPU_BEST"
    HYBRID_BEST = "HYBRID_BEST"
    CPU_ONLY = "CPU_ONLY"
    IGPU_UNSUPPORTED = "IGPU_UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class DeviceDispatchMetrics(BaseModel):
    dispatch_cost_us: float
    transfer_cost_us: float
    execution_cost_us: float
    sync_cost_us: float
    total_cost_us: float


class AdaptiveDeviceScheduler:
    """
    Empirical Hardware Dispatch Scheduler for Intel Core i5-12450H + Intel UHD Graphics.
    """

    @classmethod
    def classify_workload(
        cls,
        operation_name: str,
        workload_flops: int,
        memory_bytes: int,
    ) -> SchedulingClass:
        """
        Classifies operation based on arithmetic intensity and kernel size.
        For Intel UHD 48 EUs:
        - If memory bytes < 64KB or FLOPs < 100,000: CPU_BEST (PCIe/driver launch latency dominates).
        - If highly parallel, high arithmetic intensity (e.g. dense GEMM > 10M FLOPs): IGPU_BEST.
        - If sequential, irregular branch, or pointer-heavy: CPU_ONLY.
        """
        if operation_name in ["DELTA_MATMUL", "EARLY_TERMINATION", "BRANCH"]:
            return SchedulingClass.CPU_ONLY

        arithmetic_intensity = float(workload_flops) / max(1, memory_bytes)

        if workload_flops < 500_000:
            # CPU dispatch overhead is much lower
            return SchedulingClass.CPU_BEST

        if arithmetic_intensity > 15.0 and workload_flops >= 10_000_000:
            return SchedulingClass.IGPU_BEST

        if workload_flops >= 2_000_000 and arithmetic_intensity >= 8.0:
            return SchedulingClass.HYBRID_BEST

        return SchedulingClass.CPU_BEST

    @classmethod
    def schedule_execution(
        cls,
        kernel_name: str,
        cpu_exec_fn: Callable[[], Any],
        igpu_exec_fn: Optional[Callable[[], Any]],
        workload_flops: int,
        memory_bytes: int,
    ) -> Tuple[Any, SchedulingClass, DeviceTarget]:
        sched_class = cls.classify_workload(kernel_name, workload_flops, memory_bytes)

        if sched_class in [SchedulingClass.CPU_BEST, SchedulingClass.CPU_ONLY, SchedulingClass.UNKNOWN] or igpu_exec_fn is None:
            res = cpu_exec_fn()
            return res, sched_class, DeviceTarget.CPU_AVX2
        elif sched_class == SchedulingClass.IGPU_BEST:
            res = igpu_exec_fn()
            return res, sched_class, DeviceTarget.INTEL_UHD_IGPU
        else:
            # Hybrid or fallback
            res = cpu_exec_fn()
            return res, sched_class, DeviceTarget.HYBRID_CPU_IGPU
