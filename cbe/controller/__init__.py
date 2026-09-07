"""
cbe/controller/__init__.py
CBE Controller Subsystem: Hardware profiling, compute budgeting, workload routing,
quality supervision, thermal management, latency pacing, and master CBE coordinator.
"""

from .hardware_profile import HardwareProfile, detect_hardware
from .compute_budget import ComputeBudget, StageBudget
from .quality_controller import QualityController, QualityContract
from .thermal_controller import ThermalController
from .latency_controller import LatencyController, LatencyReport
from .workload_controller import WorkloadController, RouteStats
from .cbe_controller import CBEController, CBECycleResult

__all__ = [
    "HardwareProfile",
    "detect_hardware",
    "ComputeBudget",
    "StageBudget",
    "QualityController",
    "QualityContract",
    "ThermalController",
    "LatencyController",
    "LatencyReport",
    "WorkloadController",
    "RouteStats",
    "CBEController",
    "CBECycleResult",
]
