"""
hyper_v2/execution/cpu_backend.py
AVX2 SIMD and multi-core CPU execution backend for HYPER 2.0.
"""

import time
import numpy as np
import torch
from typing import Dict, Any, Tuple


class CPUBackend:
    """Dispatches vectorized operations across P-cores (AVX2/FMA) and E-cores."""

    @staticmethod
    def execute_gemm_dense(A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        C = np.matmul(A, B)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return C, elapsed_ms

    @staticmethod
    def execute_fft_dense(signal: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        spectrum = np.fft.fftn(signal)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return spectrum, elapsed_ms

    @staticmethod
    def execute_reduction_simd(tensor: np.ndarray) -> Tuple[float, float]:
        t0 = time.perf_counter()
        val = float(np.sum(tensor, dtype=np.float64))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return val, elapsed_ms
