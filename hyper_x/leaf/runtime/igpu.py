"""
hyper_x/leaf/runtime/igpu.py
============================
Intel UHD Graphics (48 EUs) execution backend using OpenCL Zero-Copy UVA.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.extreme.opencl_uva import OpenCLZeroCopyUVA


class LeafiGPURuntime:
    """Intel UHD iGPU runtime utilizing pinned host zero-copy memory."""

    def __init__(self):
        self.uva = OpenCLZeroCopyUVA()

    def execute_gemm(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        return self.uva.execute_zero_copy_gemm(A, B)
