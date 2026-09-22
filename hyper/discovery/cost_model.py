"""
hyper/discovery/cost_model.py
==============================
Holistic Cost & Resource Model for HYPER.

Calculates:
  T_total = T_analysis + T_generation + T_compilation + T_execution
            + T_memory + T_synchronization + T_verification + T_reconstruction
            + P_fallback * T_fallback

Tracks physical constraints on Intel Core i5-12450H (8c/12t) + Intel UHD 48EU iGPU + 16GB RAM:
- Maximum physical memory bandwidth: 18.57 GB/s
- Thermal envelope: 45W TDP package (15W nominal sustained)
- Memory footprint: <= 16GB system RAM
- Verification and fallback penalties
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.pathway_ir import PathwayIR, ExecutionDevice


class ResourceProfile(BaseModel):
    ram_mb: float = 64.0
    cpu_utilization_pct: float = 50.0
    igpu_utilization_pct: float = 0.0
    memory_bandwidth_gb_s: float = 5.0
    cache_miss_rate_pct: float = 4.0
    power_watts: float = 15.0
    temperature_celsius: float = 55.0


class TimeBreakdown(BaseModel):
    t_analysis_ms: float = 0.05
    t_generation_ms: float = 0.10
    t_compilation_ms: float = 0.05
    t_execution_ms: float = 1.00
    t_memory_ms: float = 0.20
    t_synchronization_ms: float = 0.05
    t_verification_ms: float = 0.10
    t_reconstruction_ms: float = 0.00
    p_fallback: float = 0.001
    t_fallback_ms: float = 10.00

    @property
    def t_total_ms(self) -> float:
        return (
            self.t_analysis_ms
            + self.t_generation_ms
            + self.t_compilation_ms
            + self.t_execution_ms
            + self.t_memory_ms
            + self.t_synchronization_ms
            + self.t_verification_ms
            + self.t_reconstruction_ms
            + (self.p_fallback * self.t_fallback_ms)
        )


class CostEvaluationResult(BaseModel):
    pathway_id: str
    is_cost_viable: bool
    t_total_ms: float
    throughput_ops_sec: float
    time_breakdown: TimeBreakdown
    resource_profile: ResourceProfile
    bandwidth_exceeded: bool = False
    ram_exceeded: bool = False
    overhead_ratio: float = 0.0  # (Total - Execution) / Total
    net_speedup_vs_baseline: float = 1.0


class PathwayCostModel:
    """
    Computes rigorous end-to-end execution cost including overheads and hardware barriers.
    """

    MAX_BANDWIDTH_GB_S = 18.57  # Physical limit of DDR4/DDR5 dual-channel system memory
    MAX_SYSTEM_RAM_MB = 14336.0  # Usable slice of 16 GB unified RAM
    MAX_PACKAGE_POWER_WATTS = 45.0

    def evaluate_cost(
        self,
        pathway: PathwayIR,
        baseline_latency_ms: float = 10.0,
        bytes_transferred: int = 1024 * 1024,
    ) -> CostEvaluationResult:
        # Determine device distribution
        dev = pathway.execution_plan.primary_device
        cpu_util = 80.0 if dev in (ExecutionDevice.CPU_AVX2, ExecutionDevice.CPU_SCALAR_FALLBACK) else 30.0
        igpu_util = 75.0 if dev == ExecutionDevice.IGPU_VULKAN else (50.0 if dev == ExecutionDevice.HYBRID_CPU_IGPU else 0.0)

        # Baseline execution estimate
        base_exec_ms = pathway.cost_estimate.estimated_latency_ms
        reduction_pct = sum(t.estimated_work_reduction_pct for t in pathway.transformations)
        t_exec = max(base_exec_ms * (1.0 - min(reduction_pct, 90.0) / 100.0), 0.1)

        # Memory time based on bandwidth
        mb_moved = bytes_transferred / (1024 * 1024)
        use_wormhole = pathway.memory_plan.use_unified_wormhole
        effective_bw = min(self.MAX_BANDWIDTH_GB_S * (1.5 if use_wormhole else 1.0), 25.0)
        t_mem = (mb_moved / (effective_bw * 1024)) * 1000.0

        # Verification time
        t_verify = 0.15 if pathway.verification_plan.run_adversarial_gauntlet else 0.02

        tb = TimeBreakdown(
            t_analysis_ms=0.04,
            t_generation_ms=0.06,
            t_compilation_ms=0.05,
            t_execution_ms=t_exec,
            t_memory_ms=t_mem,
            t_synchronization_ms=0.08 if dev == ExecutionDevice.HYBRID_CPU_IGPU else 0.01,
            t_verification_ms=t_verify,
            t_reconstruction_ms=0.10 if any(t.category == "GRAPHICS" for t in pathway.transformations) else 0.0,
            p_fallback=pathway.cost_estimate.fallback_probability,
            t_fallback_ms=pathway.fallback_plan.fallback_penalty_cost_ms,
        )

        t_tot = tb.t_total_ms
        t_bandwidth_demand = (mb_moved / max(t_tot / 1000.0, 0.0001)) / 1024.0
        bw_exceeded = t_bandwidth_demand > self.MAX_BANDWIDTH_GB_S
        ram_mb = pathway.memory_plan.estimated_peak_memory_mb
        ram_exceeded = ram_mb > self.MAX_SYSTEM_RAM_MB

        res_profile = ResourceProfile(
            ram_mb=ram_mb,
            cpu_utilization_pct=cpu_util,
            igpu_utilization_pct=igpu_util,
            memory_bandwidth_gb_s=min(t_bandwidth_demand, self.MAX_BANDWIDTH_GB_S),
            cache_miss_rate_pct=2.5 if use_wormhole else 6.0,
            power_watts=15.0 + (igpu_util / 100.0) * 12.0,
            temperature_celsius=52.0 + (cpu_util / 100.0) * 15.0,
        )

        overhead = (t_tot - t_exec) / max(t_tot, 0.001)
        speedup = baseline_latency_ms / max(t_tot, 0.001)
        viable = (speedup > 1.0 or t_tot < baseline_latency_ms) and not ram_exceeded

        return CostEvaluationResult(
            pathway_id=pathway.pathway_id,
            is_cost_viable=viable,
            t_total_ms=t_tot,
            throughput_ops_sec=1000.0 / max(t_tot, 0.001),
            time_breakdown=tb,
            resource_profile=res_profile,
            bandwidth_exceeded=bw_exceeded,
            ram_exceeded=ram_exceeded,
            overhead_ratio=overhead,
            net_speedup_vs_baseline=speedup,
        )
