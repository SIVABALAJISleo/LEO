"""
hyper/upe/execution.py
======================
ENGINE 10: Resource-Aware Execution & ENGINE 11: Memory/Data-Movement Escape.

Planners and executors aware of host silicon:
- Intel Core i5 (Performance Cores + Efficient Cores, AVX2 SIMD)
- Intel UHD Graphics integrated GPU
- Shared System DDR RAM (UMA zero-copy ring)
- 256 KB Driver Dispatch Latency Threshold:
  Tasks < 256 KB execute directly on CPU AVX2 to avoid 15-50 us driver queue launch overhead.
  Tasks >= 256 KB are eligible for iGPU/OpenVINO acceleration.
- Out-of-core memory chunking: limits resident working set to L2 cache blocks (256 KB).
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import os
import platform
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import psutil
import numpy as np

from hyper.hardware import get_hardware_profile


class ExecutionTarget(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_IGPU_OPENVINO = "INTEL_IGPU_OPENVINO"
    CPU_FALLBACK = "CPU_FALLBACK"


@dataclasses.dataclass
class HostResourceState:
    cpu_model: str
    physical_cores: int
    logical_cores: int
    total_ram_gb: float
    available_ram_gb: float
    has_avx2: bool
    has_igpu: bool
    igpu_name: str
    dispatch_threshold_bytes: int = 256 * 1024  # 256 KB cutoff


@dataclasses.dataclass
class ExecutionPlan:
    workload_id: str
    data_size_bytes: int
    selected_target: ExecutionTarget
    dispatch_reason: str
    chunking_required: bool
    chunk_size_bytes: int
    zero_copy_eligible: bool


class ResourceAwareExecutionPlanner:
    """
    Schedules execution across CPU AVX2 and Intel UHD iGPU based on data scale and hardware telemetry.
    """

    def __init__(self) -> None:
        self.profile = self._detect_host_environment()

    def _detect_host_environment(self) -> HostResourceState:
        hw = get_hardware_profile()
        vmem = psutil.virtual_memory()

        cpu_name = hw.get("cpu_model", platform.processor() or "Intel Core i5")
        p_cores = hw.get("physical_cores", 8)
        l_cores = hw.get("logical_processors", 12)
        ram_gb = vmem.total / (1024**3)
        avail_gb = vmem.available / (1024**3)

        igpu_name = hw.get("gpu_model", "Intel UHD Graphics")
        has_igpu = "intel" in igpu_name.lower() or len(hw.get("openvino_devices", [])) > 1

        return HostResourceState(
            cpu_model=cpu_name,
            physical_cores=p_cores,
            logical_cores=l_cores,
            total_ram_gb=round(ram_gb, 2),
            available_ram_gb=round(avail_gb, 2),
            has_avx2=True,
            has_igpu=has_igpu,
            igpu_name=igpu_name,
        )

    def plan_execution(
        self,
        workload_id: str,
        inputs: Dict[str, Any],
        memory_budget_mb: float = 512.0,
    ) -> ExecutionPlan:
        """
        Creates an execution plan respecting the 256 KB driver latency threshold and memory ceilings.
        """
        # Calculate input size in bytes
        total_bytes = 0
        for v in inputs.values():
            if isinstance(v, np.ndarray):
                total_bytes += v.nbytes
            elif isinstance(v, (list, tuple)):
                total_bytes += len(v) * 8
            else:
                total_bytes += 1024

        threshold = self.profile.dispatch_threshold_bytes
        budget_bytes = int(memory_budget_mb * 1024 * 1024)
        chunking_required = total_bytes > budget_bytes
        chunk_size = 256 * 1024 if chunking_required else total_bytes

        # Decision rule: Sub-256 KB tasks are faster on CPU AVX2 due to queue latency
        if total_bytes < threshold:
            target = ExecutionTarget.CPU_AVX2
            reason = (
                f"Data size {total_bytes:,} bytes < 256 KB dispatch threshold. "
                f"Dispatched to CPU AVX2 zero-copy (avoids 15-50us driver queue launch latency)."
            )
        elif self.profile.has_igpu:
            # Large enough for iGPU/OpenVINO
            target = ExecutionTarget.INTEL_IGPU_OPENVINO
            reason = (
                f"Data size {total_bytes:,} bytes >= 256 KB dispatch threshold. "
                f"Eligible for Intel UHD iGPU / OpenVINO acceleration."
            )
        else:
            target = ExecutionTarget.CPU_AVX2
            reason = "iGPU unavailable; running on CPU AVX2."

        return ExecutionPlan(
            workload_id=workload_id,
            data_size_bytes=total_bytes,
            selected_target=target,
            dispatch_reason=reason,
            chunking_required=chunking_required,
            chunk_size_bytes=chunk_size,
            zero_copy_eligible=True,
        )
