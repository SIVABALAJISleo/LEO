"""
hyper/discovery/scheduler.py
============================
Resource-Aware CPU + iGPU Execution Engine and Scheduler.

Manages execution across:
- CPU (Multi-core P+E hybrid architecture)
- iGPU (Intel UHD Graphics with shared system memory)
- Memory bandwidth & thermal constraints

Scientific Rule:
Never claims that CPU+iGPU creates dedicated GPU hardware.
"""

from __future__ import annotations

import dataclasses
import enum
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from hyper.discovery.cir import CIRGraph
from hyper.discovery.cost_model import CostModel, MeasuredCost, PredictedCost
from hyper.hardware import get_hardware_profile


class DeviceTarget(str, enum.Enum):
    CPU_ONLY = "CPU_ONLY"
    IGPU_ONLY = "IGPU_ONLY"
    HETEROGENEOUS_CPU_IGPU = "HETEROGENEOUS_CPU_IGPU"


class ExecutionSchedule(str, enum.Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    PIPELINE = "PIPELINE"


@dataclasses.dataclass
class SchedulingDecision:
    target_device: DeviceTarget
    schedule_mode: ExecutionSchedule
    predicted_cost: PredictedCost
    rationalization: str
    hardware_disclaimer: str = (
        "SCIENTIFIC NOTICE: Execution utilizes local CPU/iGPU shared memory resources. "
        "Performance parity does not imply hardware parity."
    )


class ResourceAwareScheduler:
    """
    Resource-aware scheduler across CPU, iGPU, and RAM.
    """

    def __init__(self, cost_model: Optional[CostModel] = None):
        self.cost_model = cost_model or CostModel()
        self.hw_profile = get_hardware_profile()
        self.has_igpu = self.hw_profile.get("gpu_model") is not None
        self.openvino_devices = self.hw_profile.get("openvino_devices", [])

    def schedule_workload(self, graph: CIRGraph) -> SchedulingDecision:
        """
        Decide optimal execution target based on arithmetic intensity and problem scale.
        """
        pred = self.cost_model.predict_cost(graph)

        # Heuristic 1: Small workloads (< 100K FLOPs) or memory-bound (intensity < 0.5)
        # Avoid device offload overhead by pinning to CPU
        if pred.estimated_flops < 1e5 or pred.arithmetic_intensity_flops_per_byte < 0.5:
            return SchedulingDecision(
                target_device=DeviceTarget.CPU_ONLY,
                schedule_mode=ExecutionSchedule.SEQUENTIAL,
                predicted_cost=pred,
                rationalization=(
                    f"Selected CPU_ONLY: Workload scale ({pred.estimated_flops:.0f} FLOPs) "
                    f"or low arithmetic intensity ({pred.arithmetic_intensity_flops_per_byte:.2f} FLOP/B) "
                    f"makes device offload transfer latency disadvantageous."
                ),
            )

        # Heuristic 2: Compute-intensive workload (> 1M FLOPs) with available iGPU
        if "GPU" in self.openvino_devices and pred.estimated_flops >= 1e6:
            return SchedulingDecision(
                target_device=DeviceTarget.IGPU_ONLY,
                schedule_mode=ExecutionSchedule.SEQUENTIAL,
                predicted_cost=pred,
                rationalization=(
                    f"Selected IGPU_ONLY: High arithmetic intensity ({pred.arithmetic_intensity_flops_per_byte:.2f} FLOP/B) "
                    f"and {pred.estimated_flops:.0f} FLOPs benefit from Intel UHD parallel execution units."
                ),
            )

        # Heuristic 3: Default CPU multi-threaded execution
        return SchedulingDecision(
            target_device=DeviceTarget.CPU_ONLY,
            schedule_mode=ExecutionSchedule.PARALLEL,
            predicted_cost=pred,
            rationalization="Selected CPU_ONLY multi-threaded execution across P+E hybrid cores.",
        )

    def execute(self, graph: CIRGraph, inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], MeasuredCost, SchedulingDecision]:
        """
        Schedule and execute graph, measuring actual latency and memory footprint.
        """
        decision = self.schedule_workload(graph)
        dev_str = "CPU" if decision.target_device == DeviceTarget.CPU_ONLY else "iGPU"

        outputs, measured = self.cost_model.measure_cost(
            graph=graph,
            inputs=inputs,
            device=dev_str,
            repetitions=3,
            warmup=1,
        )

        return outputs, measured, decision
