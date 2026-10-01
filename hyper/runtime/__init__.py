"""
hyper/runtime
=============
Adaptive Execution and Runtime Infrastructure for LEO/HYPER.
Fulfills Sections 66, 67, 68, 69, 70 of the Breakthrough Master Architecture.
"""

from .adaptive_runtime import AdaptiveRuntime, ExecutionBackend, ThermalTelemetry

__all__ = [
    "AdaptiveRuntime",
    "ExecutionBackend",
    "ThermalTelemetry",
]
