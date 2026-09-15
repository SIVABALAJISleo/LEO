"""
hyper_x/leaf/runtime/hybrid.py
==============================
Pipelined CPU + Intel UHD co-processing backend.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .cpu import LeafCPURuntime
from .igpu import LeafiGPURuntime


class LeafHybridRuntime:
    """Pipelines work across CPU and Intel UHD iGPU without memory copy overhead."""

    def __init__(self):
        self.cpu = LeafCPURuntime()
        self.igpu = LeafiGPURuntime()

    def execute_partitioned(
        self,
        A: np.ndarray,
        B: np.ndarray,
        cpu_ratio: float = 0.5,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Splits matrix rows between CPU and Intel UHD."""
        M, K = A.shape
        split = int(M * cpu_ratio)

        A_cpu = A[:split]
        A_gpu = A[split:]

        C_cpu, meta_cpu = self.cpu.execute(lambda: np.matmul(A_cpu, B))
        C_gpu, meta_gpu = self.igpu.execute_gemm(A_gpu, B)

        C = np.vstack([C_cpu, C_gpu])
        return C, {
            "backend": "HYBRID_CPU_UHD_PIPELINED",
            "cpu_rows": split,
            "gpu_rows": M - split,
            "cpu_meta": meta_cpu,
            "gpu_meta": meta_gpu,
        }
