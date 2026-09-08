"""
hyper_x/wormhole_compiler/cost_model.py
=============================================================================
HYPER-X Multi-Dimensional Hardware Execution Cost Model
=============================================================================
Goes beyond FLOPs alone to model:
  - Arithmetic FLOPs & SIMD/AVX2 vectorization efficiency
  - Memory traffic across L1, L2, L3 cache and main system RAM
  - Cache misses & TLB thrashing penalty
  - Synchronization & thread lock contention
  - Branch divergence & masking cost
  - CPU vs Intel iGPU utilization
  - Host-to-device PCIe/shared-memory transfer overhead
  - OpenVINO/OpenCL kernel compilation & launch overhead
  - Preprocessing, correction, and verification overhead

Evaluates the multi-objective cost objective:
  J = wc * compute_cost
    + wm * memory_cost
    + wl * latency
    + we * energy
    + wq * quality_penalty
    + wr * verification_cost
    + wx * communication_cost
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from hyper_x.wormhole_compiler.schemas import CostVector, WorkloadContract


class HardwareCostModel:
    """Hardware-aware performance and resource cost estimator."""

    def __init__(
        self,
        ram_bandwidth_gb_s: float = 45.0,
        l3_bandwidth_gb_s: float = 150.0,
        cpu_peak_gflops: float = 250.0,
        igpu_peak_gflops: float = 650.0,
        kernel_launch_overhead_ms: float = 0.035,
        shared_memory_transfer_rate_gb_s: float = 30.0
    ):
        self.ram_bw = ram_bandwidth_gb_s
        self.l3_bw = l3_bandwidth_gb_s
        self.cpu_flops = cpu_peak_gflops
        self.igpu_flops = igpu_peak_gflops
        self.launch_overhead_ms = kernel_launch_overhead_ms
        self.transfer_bw = shared_memory_transfer_rate_gb_s

    def evaluate_cost(
        self,
        nominal_flops: float,
        actual_flops: float,
        bytes_transferred: int,
        partition_ratio_igpu: float,
        requires_verification: bool = True,
        verification_flops: float = 0.0,
        preprocessing_ms: float = 0.0,
        correction_ms: float = 0.0
    ) -> CostVector:
        """Calculates multi-factor cost vector for a candidate pathway."""
        # Arithmetic time
        cpu_share = 1.0 - partition_ratio_igpu
        igpu_share = partition_ratio_igpu

        cpu_arith_time_ms = (actual_flops * cpu_share / (self.cpu_flops * 1e6)) if cpu_share > 0 else 0.0
        igpu_arith_time_ms = (actual_flops * igpu_share / (self.igpu_flops * 1e6)) if igpu_share > 0 else 0.0
        launch_ms = self.launch_overhead_ms if igpu_share > 0 else 0.0

        # Memory transfer & bandwidth
        mem_gb = bytes_transferred / (1024**3)
        mem_time_ms = (mem_gb / self.ram_bw) * 1000.0

        # Transfer time for iGPU portion if not zero-copy
        transfer_ms = (mem_gb * igpu_share / self.transfer_bw) * 1000.0 if igpu_share > 0 else 0.0

        # Verification overhead (e.g. Freivalds O(N^2))
        verify_ms = (verification_flops / (self.cpu_flops * 1e6)) if requires_verification else 0.0

        # Total latency: max of compute streams + memory/transfer overheads
        active_compute_ms = max(cpu_arith_time_ms, igpu_arith_time_ms + launch_ms)
        total_latency_ms = active_compute_ms + (0.3 * mem_time_ms) + transfer_ms + preprocessing_ms + correction_ms + verify_ms

        # Energy estimate: 28W CPU + 15W iGPU nominal active power
        avg_power_watts = (28.0 * cpu_share) + (15.0 * igpu_share) + 5.0
        energy_joules = avg_power_watts * (total_latency_ms / 1000.0)

        return CostVector(
            arithmetic_cost=actual_flops,
            memory_traffic_bytes=float(bytes_transferred),
            cache_miss_estimate=bytes_transferred * 0.1,
            synchronization_overhead=0.05 if (0.0 < partition_ratio_igpu < 1.0) else 0.0,
            branch_divergence_cost=0.0,
            vectorization_efficiency=0.92,
            cpu_utilization=cpu_share,
            igpu_utilization=igpu_share,
            transfer_overhead_ms=transfer_ms,
            kernel_launch_overhead_ms=launch_ms,
            communication_cost=transfer_ms * 1.5,
            preprocessing_overhead_ms=preprocessing_ms,
            postprocessing_overhead_ms=0.0,
            verification_overhead_ms=verify_ms,
            correction_overhead_ms=correction_ms,
            total_latency_ms=total_latency_ms,
            estimated_energy_joules=energy_joules
        )

    def compute_objective_j(
        self,
        cost: CostVector,
        contract: WorkloadContract,
        error: float
    ) -> float:
        """Computes contract-weighted scalar objective J."""
        # Adapt weights to contract SLO and tolerance
        wc = 1.0
        wm = 0.5
        wl = 3.0 if cost.total_latency_ms > contract.latency_slo_ms else 1.0
        we = 0.1
        wq = 100.0 if error > contract.tolerance else 1.0
        wr = 0.2
        wx = 0.5

        quality_penalty = max(0.0, error - contract.tolerance) * 1000.0
        return cost.compute_weighted_scalar(wc, wm, wl, we, wq, wr, wx, quality_penalty)
