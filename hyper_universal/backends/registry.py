"""
hyper_universal/backends/registry.py
Hardware Backend Capability Registry:
Discovers and registers actual local execution hardware (AVX2 CPU, Intel UHD iGPU via OpenCL/Vulkan),
strictly validating runtime driver availability before allowing dispatch.
"""
from __future__ import annotations
import platform
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import numpy as np

from hyper_omega.scheduler.heterogeneous import IntelHardwareScheduler, HardwareTarget


@dataclass
class BackendCapability:
    target: HardwareTarget
    is_available: bool
    description: str
    supported_dtypes: List[str]
    peak_bandwidth_gbps: float
    requires_compilation: bool = False
    is_native_gpu: bool = False
    max_ram_bytes: int = 16 * 1024 * 1024 * 1024

    @property
    def backend_name(self) -> str:
        return self.target.value

    @property
    def device_type(self) -> str:
        return "GPU" if self.is_native_gpu else "CPU"

    @property
    def max_memory_mb(self) -> float:
        return self.max_ram_bytes / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend_name": self.backend_name,
            "target": self.target.value,
            "is_available": self.is_available,
            "device_type": self.device_type,
            "description": self.description,
            "supported_dtypes": self.supported_dtypes,
            "peak_bandwidth_gbps": round(self.peak_bandwidth_gbps, 2),
            "max_memory_mb": round(self.max_memory_mb, 2),
            "is_native_gpu": self.is_native_gpu,
        }


class BackendCapabilityRegistry:
    """Queries, detects, and registers physical host compute capabilities."""

    def __init__(self):
        self._capabilities: Dict[HardwareTarget, BackendCapability] = {}
        self._discover()

    def _discover(self):
        hw_info = IntelHardwareScheduler.discover_hardware_backends()
        ram_bw = hw_info["measured_ram_bandwidth_gbps"]

        # CPU AVX2 is always available on target Intel Core i5
        self._capabilities[HardwareTarget.CPU_AVX2] = BackendCapability(
            target=HardwareTarget.CPU_AVX2,
            is_available=True,
            description="Intel Core i5 AVX2 host execution (4P+4E/12T)",
            supported_dtypes=["float64", "float32", "float16", "int32", "int8"],
            peak_bandwidth_gbps=ram_bw,
            requires_compilation=False,
            is_native_gpu=False,
        )

        # OpenCL on Intel UHD iGPU
        self._capabilities[HardwareTarget.INTEL_UHD_IGPU_OPENCL] = BackendCapability(
            target=HardwareTarget.INTEL_UHD_IGPU_OPENCL,
            is_available=hw_info["opencl_available"],
            description="Intel UHD Graphics via OpenCL",
            supported_dtypes=["float32", "int32"],
            peak_bandwidth_gbps=ram_bw,
            requires_compilation=True,
            is_native_gpu=hw_info["opencl_available"],
        )

        # Vulkan on Intel UHD iGPU
        self._capabilities[HardwareTarget.INTEL_UHD_IGPU_VULKAN] = BackendCapability(
            target=HardwareTarget.INTEL_UHD_IGPU_VULKAN,
            is_available=hw_info["vulkan_available"],
            description="Intel UHD Graphics via Vulkan Compute",
            supported_dtypes=["float32", "int32"],
            peak_bandwidth_gbps=ram_bw,
            requires_compilation=True,
            is_native_gpu=hw_info["vulkan_available"],
        )

        # CPU Fallback
        self._capabilities[HardwareTarget.CPU_FALLBACK] = BackendCapability(
            target=HardwareTarget.CPU_FALLBACK,
            is_available=True,
            description="CPU Fallback safe reference execution",
            supported_dtypes=["float64", "float32", "float16", "int32", "int8"],
            peak_bandwidth_gbps=ram_bw,
            requires_compilation=False,
            is_native_gpu=False,
        )

    def get_capability(self, target: HardwareTarget) -> Optional[BackendCapability]:
        return self._capabilities.get(target)

    def get_backend(self, name_or_target: Union[str, HardwareTarget]) -> Optional[BackendCapability]:
        if isinstance(name_or_target, HardwareTarget):
            return self._capabilities.get(name_or_target)
        for target, cap in self._capabilities.items():
            if target.value == name_or_target or target.name == name_or_target:
                return cap
        return None

    def get_available_backends(self) -> List[BackendCapability]:
        return [cap for cap in self._capabilities.values() if cap.is_available]

    def list_available_targets(self) -> List[HardwareTarget]:
        return [target for target, cap in self._capabilities.items() if cap.is_available]

    def to_dict(self) -> Dict[str, Any]:
        return {
            target.value: cap.to_dict()
            for target, cap in self._capabilities.items()
        }
