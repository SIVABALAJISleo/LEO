"""
hyper/escape_engine/analysis/memory_model.py
============================================
VAEE Memory Footprint, Cache Line & Bandwidth Model.
Models memory traffic against the measured 18.57 GB/s physical bus of Intel Core i5-12450H.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, Tuple
import numpy as np


@dataclasses.dataclass
class MemoryTrafficProfile:
    total_bytes_read: int
    total_bytes_written: int
    cache_miss_estimate: int
    bus_saturation_ratio: float       # Ratio of required throughput vs 18.57 GB/s ceiling
    is_memory_bound: bool


class MemoryModel:
    """Models memory traffic, cache alignment, and bus utilization."""

    MEASURED_BUS_BANDWIDTH_GBPS = 18.57  # Live STREAM benchmark median from hardware_profile.yaml

    @staticmethod
    def evaluate_gemm_traffic(M: int, K: int, N: int, duration_ms: float, dtype_bytes: int = 4) -> MemoryTrafficProfile:
        # Naive minimum data movement: Read A (M*K), Read B (K*N), Write C (M*N)
        read_bytes = (M * K + K * N) * dtype_bytes
        write_bytes = (M * N) * dtype_bytes
        total_bytes = read_bytes + write_bytes

        # Sustained bandwidth in GB/s
        dur_s = max(1e-7, duration_ms / 1000.0)
        achieved_gbps = (total_bytes / (1024 ** 3)) / dur_s

        bus_ratio = achieved_gbps / MemoryModel.MEASURED_BUS_BANDWIDTH_GBPS
        is_mem_bound = bus_ratio > 0.50

        # Cache line misses estimate (64 bytes per cache line)
        miss_est = total_bytes // 64

        return MemoryTrafficProfile(
            total_bytes_read=read_bytes,
            total_bytes_written=write_bytes,
            cache_miss_estimate=miss_est,
            bus_saturation_ratio=round(bus_ratio, 3),
            is_memory_bound=is_mem_bound,
        )
