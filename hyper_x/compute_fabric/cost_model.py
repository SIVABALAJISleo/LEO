#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/cost_model.py
====================================
Project Omega: Software-Defined Parallel Compute Fabric.
Empirical & Theoretical Live Cost Model for CPU, Intel UHD, RAM, and Caches.
"""

from __future__ import annotations
import math
from typing import Dict, Any, Optional
from hyper_x.compute_fabric.work_unit import WorkUnit, ExecutionTarget, LocalityClass


class FabricCostModel:
    """
    Live cost model tracking arithmetic operations, memory traffic,
    cache hierarchies, synchronization, and kernel launch overheads.
    """

    # Target hardware empirical baselines: Intel Core i5-12450H + UHD Graphics
    CPU_PEAK_GFLOPS_FP32 = 450.0   # 4 P-cores + 4 E-cores with AVX2/FMA
    UHD_PEAK_GFLOPS_FP32 = 650.0   # 48 Execution Units @ 1.20 GHz FP32
    RAM_BANDWIDTH_GB_S = 51.2      # 16 GB DDR4/DDR5 Dual-Channel
    L1_BANDWIDTH_GB_S = 800.0
    L2_BANDWIDTH_GB_S = 400.0
    L3_BANDWIDTH_GB_S = 200.0

    # Overheads in milliseconds
    CPU_LAUNCH_OVERHEAD_MS = 0.002
    UHD_LAUNCH_OVERHEAD_MS = 0.035
    EXACT_CACHE_LOOKUP_MS = 0.0005
    SYNCHRONIZATION_COST_MS = 0.005

    def __init__(self):
        # Empirical moving averages for dynamic calibration
        self.empirical_target_speedups: Dict[str, float] = {
            ExecutionTarget.CPU.value: 1.0,
            ExecutionTarget.UHD.value: 1.0,
            ExecutionTarget.CACHE.value: 1.0,
            ExecutionTarget.PREDICTOR.value: 1.0,
            ExecutionTarget.RECONSTRUCTOR.value: 1.0
        }
        self.total_evaluations: int = 0

    def estimate_cost(self, unit: WorkUnit, target: Optional[ExecutionTarget] = None) -> float:
        """
        Estimates the execution time in milliseconds for a work unit on a specific target.
        """
        tgt = target or unit.execution_target
        flops = max(unit.estimated_cost, 1.0)
        bytes_transferred = max(unit.memory_cost, 64)

        if tgt == ExecutionTarget.CACHE:
            return self.EXACT_CACHE_LOOKUP_MS

        # Compute arithmetic latency
        if tgt == ExecutionTarget.UHD:
            compute_ms = (flops / (self.UHD_PEAK_GFLOPS_FP32 * 1e6))
            launch_ms = self.UHD_LAUNCH_OVERHEAD_MS
        else:
            compute_ms = (flops / (self.CPU_PEAK_GFLOPS_FP32 * 1e6))
            launch_ms = self.CPU_LAUNCH_OVERHEAD_MS

        # Compute memory latency based on locality class
        if unit.locality == LocalityClass.L1:
            bw = self.L1_BANDWIDTH_GB_S
        elif unit.locality == LocalityClass.L2:
            bw = self.L2_BANDWIDTH_GB_S
        elif unit.locality == LocalityClass.L3:
            bw = self.L3_BANDWIDTH_GB_S
        else:
            bw = self.RAM_BANDWIDTH_GB_S

        memory_ms = (bytes_transferred / (bw * 1e6))

        # Total latency under roofline model + dispatch overhead
        base_estimate = max(compute_ms, memory_ms) + launch_ms + self.SYNCHRONIZATION_COST_MS
        calibrated_estimate = base_estimate * self.empirical_target_speedups.get(tgt.value, 1.0)
        return float(calibrated_estimate)

    def update_empirical_measurement(self, target: ExecutionTarget, estimated_ms: float, measured_ms: float):
        """Self-calibrates the cost model using real execution telemetry."""
        if estimated_ms <= 0 or measured_ms <= 0:
            return
        ratio = measured_ms / estimated_ms
        current = self.empirical_target_speedups.get(target.value, 1.0)
        # Exponential moving average with alpha = 0.1
        self.empirical_target_speedups[target.value] = 0.9 * current + 0.1 * ratio
        self.total_evaluations += 1

    def select_cheapest_target(self, unit: WorkUnit) -> ExecutionTarget:
        """Determines the optimal execution target for a work unit."""
        if unit.classification.value in ["CAN_REUSE", "CAN_ELIMINATE"]:
            return ExecutionTarget.CACHE

        cpu_cost = self.estimate_cost(unit, ExecutionTarget.CPU)
        uhd_cost = self.estimate_cost(unit, ExecutionTarget.UHD)

        # UHD is advantageous for large arithmetic densities; CPU for small/latency-sensitive units
        if uhd_cost < cpu_cost:
            return ExecutionTarget.UHD
        return ExecutionTarget.CPU
