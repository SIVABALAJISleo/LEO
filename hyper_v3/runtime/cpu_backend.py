"""
hyper_v3/runtime/cpu_backend.py
AVX2 SIMD and multi-core CPU execution backend for HYPER 3.0.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple


class CPUBackend:
    """Dispatches vectorized workloads to the host Intel CPU using multi-threaded BLAS."""

    @staticmethod
    def execute_matmul(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        c = np.matmul(a, b)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return c, elapsed_us

    @staticmethod
    def execute_fft(signal: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        res = np.fft.fft(signal)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return res, elapsed_us

    @staticmethod
    def execute_reduction(vector: np.ndarray) -> Tuple[float, float]:
        t0 = time.perf_counter()
        res = float(np.sum(vector))
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return res, elapsed_us
