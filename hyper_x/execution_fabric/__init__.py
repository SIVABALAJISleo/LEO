"""
hyper_x.execution_fabric
========================
Heterogeneous CPU + Intel UHD Computational Execution Fabric.
"""

from .capability_detector import CapabilityDetector, HardwareProfile
from .cpu_scheduler import CPUScheduler
from .igpu_scheduler import IGPUScheduler
from .heterogeneous_scheduler import HeterogeneousScheduler, ExecutionDevice
from .memory_planner import MemoryPlanner
from .kernel_dispatch import KernelDispatch
from .telemetry import FabricTelemetry

__all__ = [
    "CapabilityDetector",
    "HardwareProfile",
    "CPUScheduler",
    "IGPUScheduler",
    "HeterogeneousScheduler",
    "ExecutionDevice",
    "MemoryPlanner",
    "KernelDispatch",
    "FabricTelemetry",
]
