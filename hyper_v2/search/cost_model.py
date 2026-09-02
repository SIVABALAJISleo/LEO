"""
hyper_v2/search/cost_model.py
Predictive hardware-calibrated cost model incorporating compute, memory bandwidth, PCIe/USM transfers, and kernel launch overheads.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from hyper_v2.compiler.intermediate_representation import DeviceTarget, OpCategory


@dataclass
class CostBreakdown:
    strategy_name: str
    target_device: DeviceTarget
    estimated_compute_ms: float
    estimated_memory_ms: float
    estimated_transfer_ms: float
    estimated_overhead_ms: float
    total_estimated_latency_ms: float
    estimated_energy_joules: float
    estimated_error_bound: float
    is_contract_viable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "target_device": self.target_device.value,
            "compute_ms": round(self.estimated_compute_ms, 3),
            "memory_ms": round(self.estimated_memory_ms, 3),
            "transfer_ms": round(self.estimated_transfer_ms, 3),
            "overhead_ms": round(self.estimated_overhead_ms, 3),
            "total_latency_ms": round(self.total_estimated_latency_ms, 3),
            "energy_joules": round(self.estimated_energy_joules, 4),
            "error_bound": self.estimated_error_bound,
            "contract_viable": self.is_contract_viable
        }


class PredictiveCostModel:
    """Calculates realistic hardware execution costs across CPU and Intel UHD iGPU."""

    # Hardware specs for Intel Core i5-13420H / i5-12450H + Intel UHD 48 EU
    CPU_FP32_GFLOPS = 250.0        # AVX2 8-core peak sustained
    IGPU_FP32_GFLOPS = 1200.0      # OpenVINO Intel UHD Graphics
    SYSTEM_RAM_BW_GBS = 51.2       # DDR5 dual channel
    IGPU_USM_COPY_BW_GBS = 40.0    # Shared memory zero-copy / USM
    KERNEL_LAUNCH_OVERHEAD_MS = 0.015

    @classmethod
    def evaluate_strategy_cost(
        cls,
        strategy_name: str,
        flops: int,
        bytes_read: int,
        bytes_written: int,
        device: DeviceTarget,
        tolerance_budget: float,
        error_estimate: float = 0.0
    ) -> CostBreakdown:
        # 1. Compute time
        peak_gflops = cls.IGPU_FP32_GFLOPS if device == DeviceTarget.INTEL_IGPU else cls.CPU_FP32_GFLOPS
        if device == DeviceTarget.HYBRID_CPU_IGPU:
            peak_gflops = cls.CPU_FP32_GFLOPS * 0.4 + cls.IGPU_FP32_GFLOPS * 0.6

        compute_sec = (flops / 1e9) / max(1.0, peak_gflops * 0.70)  # 70% efficiency assumption
        compute_ms = compute_sec * 1000.0

        # 2. Memory time
        total_bytes = bytes_read + bytes_written
        memory_sec = (total_bytes / 1e9) / cls.SYSTEM_RAM_BW_GBS
        memory_ms = memory_sec * 1000.0

        # 3. Transfer overhead (zero for unified RAM on i5)
        transfer_ms = 0.002  # Cache synchronization / barrier

        # 4. Kernel launch overhead
        overhead_ms = cls.KERNEL_LAUNCH_OVERHEAD_MS if device != DeviceTarget.CPU_PCORE else 0.001

        # Total latency (roofline: max of compute vs memory bound + overhead)
        total_ms = max(compute_ms, memory_ms) + transfer_ms + overhead_ms

        # Energy (TDP approx: 35W CPU/iGPU package)
        energy_joules = (total_ms / 1000.0) * 28.0

        is_viable = error_estimate <= tolerance_budget

        return CostBreakdown(
            strategy_name=strategy_name,
            target_device=device,
            estimated_compute_ms=compute_ms,
            estimated_memory_ms=memory_ms,
            estimated_transfer_ms=transfer_ms,
            estimated_overhead_ms=overhead_ms,
            total_estimated_latency_ms=total_ms,
            estimated_energy_joules=energy_joules,
            estimated_error_bound=error_estimate,
            is_contract_viable=is_viable
        )
