"""
hyper_x/wormhole_compiler/hybrid_scheduler.py
=============================================================================
CPU + Intel UHD Heterogeneous Runtime Scheduler (Section 21)
=============================================================================
Heterogeneous work partitioning for:
  CPU: Intel Core i5-12450H (8 Cores, 12 Threads, AVX2/FMA)
       Responsibilities:
         - Control flow & branching
         - Compilation & e-graph saturation
         - Algorithm synthesis & mutation
         - Verification & Freivalds randomized checks
         - Small irregular tasks
         - Scheduling & orchestration
  GPU: Intel Integrated UHD Graphics (48 EUs, shared L3/system RAM)
       Responsibilities:
         - Large regular parallel matrix/tensor contractions
         - Batch verification across candidate populations
         - Parallel filtering & mask generation
         - Spatial graphics reconstruction & blur/denoise

Empirical Partitioning Rule:
  T_cpu vs (T_transfer_to_uhd + T_uhd_compute + T_transfer_to_cpu + T_launch)
Never assume GPU is always faster!
If data dimensions are small (e.g. M, N < 128), CPU AVX2 is orders of magnitude
faster due to zero transfer latency.
"""

from __future__ import annotations
import time
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from hyper_x.wormhole_compiler.contract_ir import UniversalWorkloadContract


class TargetDevice(str, enum.Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_UHD = "INTEL_UHD"
    HYBRID_COOPERATIVE = "HYBRID_COOPERATIVE"


@dataclass
class SchedulePartitionDecision:
    workload_id: str
    selected_device: TargetDevice
    estimated_cpu_latency_ms: float
    estimated_uhd_latency_ms: float
    transfer_overhead_ms: float
    cpu_work_fraction: float  # 0.0 to 1.0
    uhd_work_fraction: float  # 0.0 to 1.0
    selection_rationale: str
    bytes_transferred: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "selected_device": self.selected_device.value,
            "estimated_cpu_latency_ms": round(self.estimated_cpu_latency_ms, 3),
            "estimated_uhd_latency_ms": round(self.estimated_uhd_latency_ms, 3),
            "transfer_overhead_ms": round(self.transfer_overhead_ms, 3),
            "cpu_work_fraction": round(self.cpu_work_fraction, 2),
            "uhd_work_fraction": round(self.uhd_work_fraction, 2),
            "selection_rationale": self.selection_rationale,
            "bytes_transferred": self.bytes_transferred,
        }


class HybridScheduler:
    """
    Profiles and schedules computation across CPU (AVX2) and Intel UHD graphics.
    """

    def __init__(self):
        # Empirical micro-architectural parameters for i5-12450H + UHD
        self.cpu_avx2_gflops = 350.0       # Effective AVX2 FP32 throughput
        self.uhd_compute_gflops = 650.0     # 48 EUs peak compute throughput
        self.unified_mem_bandwidth_gbps = 38.0  # Shared DDR4/DDR5 system bus
        self.kernel_launch_overhead_ms = 0.08    # OpenCL/Level0 driver dispatch overhead

    def estimate_latencies(
        self,
        flops: float,
        input_bytes: float,
        output_bytes: float,
    ) -> Tuple[float, float, float]:
        """Returns (cpu_lat_ms, uhd_lat_ms, transfer_ms)."""
        # CPU compute latency
        t_cpu_ms = (flops / (self.cpu_avx2_gflops * 1e6))

        # UHD transfer & compute latency
        # Because UHD shares system RAM on Intel laptop, zero-copy buffer mapping is possible,
        # but cache invalidation / synchronization takes time
        total_transfer_bytes = input_bytes + output_bytes
        t_transfer_ms = (total_transfer_bytes / (self.unified_mem_bandwidth_gbps * 1e6))
        t_uhd_compute_ms = (flops / (self.uhd_compute_gflops * 1e6))
        t_uhd_total_ms = t_transfer_ms + t_uhd_compute_ms + self.kernel_launch_overhead_ms

        return t_cpu_ms, t_uhd_total_ms, t_transfer_ms

    def partition_workload(
        self,
        workload_id: str,
        flops: float,
        input_bytes: float,
        output_bytes: float,
        irregular_branching: bool = False,
    ) -> SchedulePartitionDecision:
        t_cpu_ms, t_uhd_ms, t_trans_ms = self.estimate_latencies(flops, input_bytes, output_bytes)

        if irregular_branching:
            return SchedulePartitionDecision(
                workload_id=workload_id,
                selected_device=TargetDevice.CPU_AVX2,
                estimated_cpu_latency_ms=t_cpu_ms,
                estimated_uhd_latency_ms=t_uhd_ms * 2.5,  # Divergent branching heavily penalizes SIMD EUs
                transfer_overhead_ms=0.0,
                cpu_work_fraction=1.0,
                uhd_work_fraction=0.0,
                selection_rationale="Irregular control flow scheduled on CPU AVX2 to prevent GPU warp divergence",
                bytes_transferred=0.0,
            )

        if t_cpu_ms <= t_uhd_ms:
            return SchedulePartitionDecision(
                workload_id=workload_id,
                selected_device=TargetDevice.CPU_AVX2,
                estimated_cpu_latency_ms=t_cpu_ms,
                estimated_uhd_latency_ms=t_uhd_ms,
                transfer_overhead_ms=0.0,
                cpu_work_fraction=1.0,
                uhd_work_fraction=0.0,
                selection_rationale="CPU AVX2 chosen: Kernel launch & transfer overhead exceeds compute benefit",
                bytes_transferred=0.0,
            )
        elif flops > 5e7:  # Large problem: cooperative split
            # Split work proportionally: 35% CPU, 65% UHD
            return SchedulePartitionDecision(
                workload_id=workload_id,
                selected_device=TargetDevice.HYBRID_COOPERATIVE,
                estimated_cpu_latency_ms=t_cpu_ms,
                estimated_uhd_latency_ms=t_uhd_ms,
                transfer_overhead_ms=t_trans_ms * 0.65,
                cpu_work_fraction=0.35,
                uhd_work_fraction=0.65,
                selection_rationale="Cooperative partition: Overlapping CPU search with UHD parallel execution",
                bytes_transferred=input_bytes * 0.65,
            )
        else:
            return SchedulePartitionDecision(
                workload_id=workload_id,
                selected_device=TargetDevice.INTEL_UHD,
                estimated_cpu_latency_ms=t_cpu_ms,
                estimated_uhd_latency_ms=t_uhd_ms,
                transfer_overhead_ms=t_trans_ms,
                cpu_work_fraction=0.0,
                uhd_work_fraction=1.0,
                selection_rationale="Intel UHD selected: Compute density sufficiently high to amortize dispatch",
                bytes_transferred=input_bytes + output_bytes,
            )
