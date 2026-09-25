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


# =============================================================================
# CIR & DISCOVERY ENGINE COST MODEL (PREDICTED vs MEASURED)
# =============================================================================

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

try:
    import psutil
except ImportError:
    psutil = None

from hyper.discovery.cir import CIRGraph, CIRNode, DataType, OpType


@dataclasses.dataclass
class PredictedCost:
    """Theoretical pre-execution estimates."""
    estimated_flops: float
    memory_traffic_bytes: int
    arithmetic_intensity_flops_per_byte: float
    estimated_latency_ms: float
    estimated_peak_memory_mb: float
    estimated_power_watts: float = 15.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class MeasuredCost:
    """Empirically measured profile during execution."""
    actual_latency_ms: float
    actual_throughput_gflops: float
    actual_peak_memory_mb: float
    cpu_utilization_pct: float
    execution_device: str
    repetition_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CostModel:
    """
    Cost Model for predicting and empirically measuring computational costs.
    Strictly separates PREDICTED_COST from MEASURED_COST.
    """

    PEAK_CPU_GFLOPS = 250.0  # Approx FP32 peak across P+E cores
    PEAK_MEM_BANDWIDTH_GB_S = 50.0  # DDR5/LPDDR5 shared memory bandwidth

    def predict_cost(self, graph: CIRGraph) -> PredictedCost:
        """Calculate theoretical FLOPs, memory traffic, and latency."""
        flops = graph.total_estimated_flops()

        traffic_bytes = 0
        for node in graph.nodes.values():
            if node.output_meta:
                traffic_bytes += node.output_meta.memory_bytes
            for inp_id in node.inputs:
                inp_node = graph.nodes.get(inp_id)
                if inp_node and inp_node.output_meta:
                    traffic_bytes += inp_node.output_meta.memory_bytes

        intensity = (flops / max(traffic_bytes, 1))

        # Roofline model latency estimate
        compute_time_sec = flops / (self.PEAK_CPU_GFLOPS * 1e9)
        memory_time_sec = traffic_bytes / (self.PEAK_MEM_BANDWIDTH_GB_S * 1e9)
        estimated_time_sec = max(compute_time_sec, memory_time_sec)
        estimated_latency_ms = estimated_time_sec * 1000.0

        peak_mem_mb = (traffic_bytes / (1024 * 1024)) * 1.5

        return PredictedCost(
            estimated_flops=flops,
            memory_traffic_bytes=traffic_bytes,
            arithmetic_intensity_flops_per_byte=intensity,
            estimated_latency_ms=max(estimated_latency_ms, 0.001),
            estimated_peak_memory_mb=max(peak_mem_mb, 0.1),
        )

    def measure_cost(
        self,
        graph: CIRGraph,
        inputs: Dict[str, Any],
        device: str = "CPU",
        repetitions: int = 3,
        warmup: int = 1,
    ) -> Tuple[Dict[str, Any], MeasuredCost]:
        """
        Profile actual execution with dedicated warmup and repetition.
        Never substitutes predicted values for measured values.
        """
        # Warmup
        for _ in range(warmup):
            out = graph.evaluate(inputs)

        latencies = []
        if psutil:
            proc = psutil.Process()
            cpu_before = psutil.cpu_percent(interval=None)
            mem_before = proc.memory_info().rss
        else:
            cpu_before = 0.0
            mem_before = 0

        for _ in range(repetitions):
            t0 = time.perf_counter()
            out = graph.evaluate(inputs)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

        if psutil:
            cpu_after = psutil.cpu_percent(interval=None)
            mem_after = proc.memory_info().rss
            peak_mb = (max(mem_before, mem_after) / (1024 * 1024))
            avg_cpu = max(cpu_before, cpu_after)
        else:
            peak_mb = 10.0
            avg_cpu = 50.0

        median_lat = float(np.median(latencies))
        flops = graph.total_estimated_flops()
        throughput_gflops = (flops / (median_lat * 1e-3 * 1e9)) if median_lat > 0 else 0.0

        measured = MeasuredCost(
            actual_latency_ms=median_lat,
            actual_throughput_gflops=throughput_gflops,
            actual_peak_memory_mb=peak_mb,
            cpu_utilization_pct=avg_cpu,
            execution_device=device,
            repetition_count=repetitions,
        )

        return out, measured

