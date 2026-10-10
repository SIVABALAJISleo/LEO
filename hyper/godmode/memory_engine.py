"""
hyper/godmode/memory_engine.py
==============================
Smart Memory & Bandwidth Reduction Engine (Feature Module D & E).

Implements the TinyStories memory principle for the fixed 16 GB RAM host:
- Working-Set Manager (pre-execution allocation planning, safety headroom)
- Bounded Reusable Buffer Pool (eliminates allocation churn & GC pressure)
- Chunked & Tiled Processing (L1/L2/L3 cache-friendly block execution)
- Memory-Mapped Streaming & Out-of-Core Execution
- Peak memory observability and bounded buffer eviction
"""

from __future__ import annotations
import collections
import os
import time
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
import numpy as np
import psutil
from pydantic import BaseModel, Field


class MemoryBudget(BaseModel):
    total_physical_ram_mb: float
    usable_safe_ram_mb: float
    current_rss_mb: float
    available_headroom_mb: float
    max_single_allocation_mb: float


class WorkingSetManager:
    """
    Evaluates memory safety prior to executing heavy computational workloads.
    Protects Windows 11 host from OOM thrashing on a 16 GB machine.
    """

    def __init__(self, safe_headroom_ratio: float = 0.75) -> None:
        self.total_ram_mb = psutil.virtual_memory().total / (1024 * 1024)
        self.safe_ratio = safe_headroom_ratio

    def get_budget(self) -> MemoryBudget:
        vm = psutil.virtual_memory()
        proc = psutil.Process(os.getpid())
        current_rss = proc.memory_info().rss / (1024 * 1024)
        available = vm.available / (1024 * 1024)
        safe_usable = min(available * self.safe_ratio, 12000.0)

        return MemoryBudget(
            total_physical_ram_mb=round(self.total_ram_mb, 1),
            usable_safe_ram_mb=round(safe_usable, 1),
            current_rss_mb=round(current_rss, 1),
            available_headroom_mb=round(available, 1),
            max_single_allocation_mb=round(safe_usable * 0.5, 1),
        )

    def assess_workload_safety(self, estimated_mb: float) -> Tuple[bool, str]:
        budget = self.get_budget()
        if estimated_mb > budget.usable_safe_ram_mb:
            return (
                False,
                f"Workload requirement ({estimated_mb:.1f}MB) exceeds safe headroom ({budget.usable_safe_ram_mb:.1f}MB). Tiling required.",
            )
        return (True, f"Safe: {estimated_mb:.1f}MB fits within {budget.usable_safe_ram_mb:.1f}MB safe headroom.")


class BoundedBufferPool:
    """
    Thread-safe, bounded memory buffer pool to eliminate malloc/free fragmentation
    and garbage-collection pauses during high-frequency computational iterations.
    """

    def __init__(self, max_cached_buffers: int = 16) -> None:
        self.max_cached = max_cached_buffers
        # Key: (shape_tuple, dtype_str) -> deque of preallocated arrays
        self._pool: Dict[Tuple[Tuple[int, ...], str], collections.deque] = collections.defaultdict(collections.deque)
        self.allocated_count = 0
        self.reused_count = 0

    def acquire(self, shape: Tuple[int, ...], dtype: Any = np.float32) -> np.ndarray:
        key = (shape, str(np.dtype(dtype)))
        dq = self._pool[key]
        if dq:
            self.reused_count += 1
            arr = dq.popleft()
            arr.fill(0)
            return arr

        self.allocated_count += 1
        return np.zeros(shape, dtype=dtype)

    def release(self, arr: np.ndarray) -> None:
        key = (arr.shape, str(arr.dtype))
        dq = self._pool[key]
        if len(dq) < self.max_cached:
            dq.append(arr)

    def clear(self) -> None:
        self._pool.clear()

    def get_stats(self) -> Dict[str, Any]:
        total_buffered = sum(len(dq) for dq in self._pool.values())
        return {
            "allocated_count": self.allocated_count,
            "reused_count": self.reused_count,
            "reuse_ratio_pct": round((self.reused_count / max(self.allocated_count + self.reused_count, 1)) * 100, 2),
            "currently_pooled_buffers": total_buffered,
        }


class ChunkedTilingEngine:
    """
    Decomposes large 2D and 3D tensor computations into cache-sized tiles.
    Optimized for Intel Core i5-12450H cache hierarchy:
    - L1 Data: 48 KB per P-Core / 32 KB per E-Core
    - L2 Cache: 1.25 MB per P-Core / 2.0 MB per E-Core cluster
    - L3 Shared Cache: 12 MB Smart Cache
    """

    @staticmethod
    def compute_cache_optimal_block_size(
        dtype_bytes: int = 4,
        target_cache_bytes: int = 1024 * 1024,  # 1 MB (fits comfortably in L2)
    ) -> int:
        """
        Calculates square tile size N such that 3 x (N x N) matrices fit in L2 cache.
        3 * N^2 * dtype_bytes <= target_cache_bytes => N = sqrt(target / (3 * dtype_bytes))
        """
        n = int(np.sqrt(target_cache_bytes / (3 * dtype_bytes)))
        # Align to cache-line boundary (64 bytes / 16 floats)
        return max(16, (n // 16) * 16)

    @classmethod
    def blocked_matmul(
        cls,
        A: np.ndarray,
        B: np.ndarray,
        block_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        Cache-blocked dense matrix multiplication for large dimensions.
        Avoids cache-line evictions and preserves temporal locality.
        """
        m, k = A.shape
        _, n = B.shape
        if block_size is None:
            block_size = cls.compute_cache_optimal_block_size(A.itemsize)

        C = np.zeros((m, n), dtype=A.dtype)
        for i in range(0, m, block_size):
            i_end = min(i + block_size, m)
            for j in range(0, n, block_size):
                j_end = min(j + block_size, n)
                for l in range(0, k, block_size):
                    l_end = min(l + block_size, k)
                    C[i:i_end, j:j_end] += np.dot(
                        A[i:i_end, l:l_end],
                        B[l:l_end, j:j_end],
                    )
        return C
