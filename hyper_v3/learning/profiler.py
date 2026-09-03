"""
hyper_v3/learning/profiler.py
Empirical micro-benchmarker for CPU SIMD, iGPU throughput, and memory bandwidth.
"""

from typing import Dict, Any
import time
import numpy as np


class HardwareProfiler:
    """Runs micro-benchmarks to calibrate real hardware characteristics."""

    @staticmethod
    def measure_memory_bandwidth_gbs(size_mb: int = 64) -> float:
        n_elems = (size_mb * 1024 * 1024) // 4
        a = np.ones(n_elems, dtype=np.float32)
        b = np.ones(n_elems, dtype=np.float32)
        
        t0 = time.perf_counter()
        c = a + b
        elapsed = time.perf_counter() - t0

        bytes_transferred = n_elems * 4 * 3  # Read A, Read B, Write C
        bw_gbs = (bytes_transferred / 1e9) / max(elapsed, 1e-6)
        return float(min(120.0, max(5.0, bw_gbs)))

    @staticmethod
    def measure_cpu_gflops(size: int = 512) -> float:
        a = np.random.randn(size, size).astype(np.float32)
        b = np.random.randn(size, size).astype(np.float32)
        flops = 2 * size * size * size

        t0 = time.perf_counter()
        c = np.matmul(a, b)
        elapsed = time.perf_counter() - t0

        gflops = (flops / 1e9) / max(elapsed, 1e-6)
        return float(gflops)
