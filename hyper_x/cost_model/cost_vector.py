"""
hyper_x/cost_model/cost_vector.py
=============================================================================
HYPER-X Hardware-Aware Cost Model & Multi-Dimensional Cost Vector
=============================================================================
Never optimize FLOPS alone.

Evaluates an 8-dimensional CostVector:
  1. compute_cost:         Arithmetic operation count (FLOPs, INT ops)
  2. memory_cost:          DRAM/VRAM traffic and cache hierarchy misses
  3. communication_cost:   PCIe/CXL/ring bus bytes moved between CPU and iGPU
  4. latency_cost:         Critical path wall-clock latency (ms)
  5. energy_cost:          Active and leakage energy consumption (Joules)
  6. synchronization_cost: Barrier stalls, queue fences, and thread synchronization
  7. startup_cost:         Kernel JIT compilation and cold pipeline initialization
  8. thermal_cost:         Thermal headroom consumed and throttling probability
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class CostVector:
    compute_cost: float        # GFLOPs or MOPs
    memory_cost: float         # Megabytes transferred through cache/DRAM
    communication_cost: float  # Megabytes over bus (CPU <-> iGPU)
    latency_cost: float        # Milliseconds execution time
    energy_cost: float         # Estimated Joules
    synchronization_cost: float# Overhead in ms
    startup_cost: float        # JIT overhead in ms
    thermal_cost: float        # Throttle risk score [0.0, 1.0]

    def scalar_cost(
        self,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Computes hardware-weighted composite cost."""
        w = weights or {
            "compute": 0.15,
            "memory": 0.25,
            "communication": 0.20,
            "latency": 0.25,
            "energy": 0.05,
            "sync": 0.05,
            "startup": 0.03,
            "thermal": 0.02
        }
        return (
            w["compute"] * self.compute_cost +
            w["memory"] * self.memory_cost +
            w["communication"] * self.communication_cost +
            w["latency"] * self.latency_cost +
            w["energy"] * self.energy_cost +
            w["sync"] * self.synchronization_cost +
            w["startup"] * self.startup_cost +
            w["thermal"] * (self.thermal_cost * 10.0)
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class HardwareCostModel:
    """Estimates CostVector for candidates given hardware characteristics."""

    def __init__(self, ram_bandwidth_gbps: float = 40.0, igpu_peak_gflops: float = 600.0):
        self.ram_bandwidth_gbps = ram_bandwidth_gbps
        self.igpu_peak_gflops = igpu_peak_gflops

    def estimate_gemm_cost(
        self,
        m: int,
        k: int,
        n: int,
        device: str = "CPU",
        sparsity: float = 0.0,
        factor_rank: Optional[int] = None
    ) -> CostVector:
        if factor_rank is not None and factor_rank < min(m, k, n):
            total_flops = 2.0 * (m * factor_rank * k + m * factor_rank * n)
            mem_mb = (m * factor_rank + factor_rank * k + factor_rank * n) * 4.0 / (1024**2)
        else:
            effective_mults = (1.0 - sparsity)
            total_flops = 2.0 * m * k * n * effective_mults
            mem_mb = (m * k + k * n + m * n) * 4.0 / (1024**2)

        gflops = total_flops / 1e9
        comm_mb = mem_mb if "GPU" in device else 0.0
        est_latency_ms = (gflops / (self.igpu_peak_gflops / 1000.0)) + (mem_mb / (self.ram_bandwidth_gbps * 1024.0) * 1000.0)
        est_energy = (est_latency_ms / 1000.0) * 15.0  # Assumes 15W TDP

        return CostVector(
            compute_cost=round(gflops, 4),
            memory_cost=round(mem_mb, 4),
            communication_cost=round(comm_mb, 4),
            latency_cost=round(est_latency_ms, 3),
            energy_cost=round(est_energy, 4),
            synchronization_cost=0.05 if "GPU" in device else 0.01,
            startup_cost=0.0,
            thermal_cost=min(1.0, est_latency_ms / 1000.0)
        )
