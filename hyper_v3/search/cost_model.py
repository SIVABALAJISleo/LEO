"""
hyper_v3/search/cost_model.py
Predictive hardware-calibrated cost model incorporating compute, bandwidth, transfer, and launch latency.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from hyper_v3.ir.operation import DeviceType


@dataclass
class CostEstimate:
    total_time_us: float
    compute_time_us: float
    memory_time_us: float
    transfer_time_us: float
    launch_overhead_us: float
    verification_overhead_us: float
    energy_relative: float


class HardwareCostModel:
    """Predictive cost model calibrated for 13th Gen Intel Core CPU + Intel UHD Graphics iGPU."""

    def __init__(
        self,
        cpu_peak_gflops: float = 350.0,
        igpu_peak_gflops: float = 600.0,
        ram_bandwidth_gbs: float = 45.0,
        usm_transfer_gbs: float = 30.0,
        igpu_launch_latency_us: float = 12.0,
        cpu_launch_latency_us: float = 1.0
    ):
        self.cpu_peak_gflops = cpu_peak_gflops
        self.igpu_peak_gflops = igpu_peak_gflops
        self.ram_bandwidth_gbs = ram_bandwidth_gbs
        self.usm_transfer_gbs = usm_transfer_gbs
        self.igpu_launch_latency_us = igpu_launch_latency_us
        self.cpu_launch_latency_us = cpu_launch_latency_us

    def estimate_cost(
        self,
        flops: int,
        read_bytes: int,
        write_bytes: int,
        device: DeviceType,
        requires_transfer: bool = False,
        requires_verification: bool = False
    ) -> CostEstimate:
        total_bytes = read_bytes + write_bytes

        if device == DeviceType.CPU:
            compute_time = (flops / (self.cpu_peak_gflops * 1e9)) * 1e6
            mem_time = (total_bytes / (self.ram_bandwidth_gbs * 1e9)) * 1e6
            transfer_time = 0.0
            launch = self.cpu_launch_latency_us
        elif device == DeviceType.IGPU:
            compute_time = (flops / (self.igpu_peak_gflops * 1e9)) * 1e6
            mem_time = (total_bytes / (self.ram_bandwidth_gbs * 1e9)) * 1e6
            transfer_time = (total_bytes / (self.usm_transfer_gbs * 1e9)) * 1e6 if requires_transfer else 0.0
            launch = self.igpu_launch_latency_us
        else:  # HYBRID (e.g. 50/50 split)
            compute_time = (flops * 0.5 / (self.cpu_peak_gflops * 1e9) + flops * 0.5 / (self.igpu_peak_gflops * 1e9)) * 0.6 * 1e6
            mem_time = (total_bytes / (self.ram_bandwidth_gbs * 1e9)) * 1e6
            transfer_time = (total_bytes * 0.5 / (self.usm_transfer_gbs * 1e9)) * 1e6 if requires_transfer else 0.0
            launch = max(self.cpu_launch_latency_us, self.igpu_launch_latency_us)

        verif_time = (compute_time * 0.1) if requires_verification else 0.0
        total_time = max(compute_time, mem_time) + transfer_time + launch + verif_time
        energy = (compute_time * 25.0 + mem_time * 10.0 + transfer_time * 5.0) / 1000.0  # Relative Joules

        return CostEstimate(
            total_time_us=total_time,
            compute_time_us=compute_time,
            memory_time_us=mem_time,
            transfer_time_us=transfer_time,
            launch_overhead_us=launch,
            verification_overhead_us=verif_time,
            energy_relative=energy
        )
