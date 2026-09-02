"""
hyper_v2/execution/scheduler.py
Dynamic scheduler routing compute tasks to CPU, Intel iGPU, or Hybrid executors.
"""

from typing import Dict, Any, Tuple
import numpy as np
from hyper_v2.compiler.intermediate_representation import DeviceTarget
from hyper_v2.execution.cpu_backend import CPUBackend
from hyper_v2.execution.igpu_backend import IntelIGPUBackend
from hyper_v2.execution.hybrid_backend import HybridBackend


class HeterogeneousScheduler:
    """Schedules and dispatches computation to optimal silicon targets."""

    @staticmethod
    def dispatch_gemm(A: np.ndarray, B: np.ndarray, device: DeviceTarget) -> Tuple[np.ndarray, float]:
        if device == DeviceTarget.INTEL_IGPU:
            return IntelIGPUBackend.execute_matmul(A, B)
        elif device == DeviceTarget.HYBRID_CPU_IGPU:
            return HybridBackend.execute_partitioned_gemm(A, B)
        else:
            return CPUBackend.execute_gemm_dense(A, B)

    @staticmethod
    def dispatch_fft(signal: np.ndarray, device: DeviceTarget) -> Tuple[np.ndarray, float]:
        if device == DeviceTarget.INTEL_IGPU:
            return IntelIGPUBackend.execute_spectral_2d(signal)
        else:
            return CPUBackend.execute_fft_dense(signal)
