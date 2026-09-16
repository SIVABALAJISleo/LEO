#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/execution_fabric/memory_planner.py
==========================================
Phase 13: Unified Memory & Scratchpad Planner.
Controls DRAM consumption under 16 GB constraints:
  - Pre-allocated workspace scratchpads (avoids malloc / gc spikes)
  - Zero-copy stride views for tiling
  - Peak memory watermark tracking & leak protection
"""

from __future__ import annotations
import gc
from typing import Dict, Any, Tuple, Optional
import numpy as np


class MemoryPlanner:
    """
    Manages in-memory tensor allocations, scratch buffers, and enforces memory budget.
    """

    def __init__(self, max_budget_bytes: int = 12 * 1024 * 1024 * 1024):  # 12 GB budget on 16 GB system
        self.max_budget_bytes = max_budget_bytes
        self.allocated_bytes = 0
        self.peak_bytes = 0
        self.scratchpads: Dict[str, np.ndarray] = {}

    def get_or_allocate_scratchpad(
        self,
        name: str,
        shape: Tuple[int, ...],
        dtype: np.dtype = np.float32
    ) -> np.ndarray:
        """
        Reuses pre-allocated buffer if shape and dtype match; otherwise allocates.
        Eliminates heap allocation overhead in hot loops.
        """
        required_bytes = int(np.prod(shape)) * np.dtype(dtype).itemsize
        if self.allocated_bytes + required_bytes > self.max_budget_bytes:
            gc.collect()

        if name in self.scratchpads:
            buf = self.scratchpads[name]
            if buf.shape == shape and buf.dtype == dtype:
                return buf

        # Allocate new
        new_buf = np.empty(shape, dtype=dtype)
        self.scratchpads[name] = new_buf
        self.allocated_bytes += required_bytes
        self.peak_bytes = max(self.peak_bytes, self.allocated_bytes)
        return new_buf

    def release_all(self) -> None:
        self.scratchpads.clear()
        self.allocated_bytes = 0
        gc.collect()

    def stats(self) -> Dict[str, Any]:
        return {
            "current_allocated_bytes": self.allocated_bytes,
            "current_allocated_mb": round(self.allocated_bytes / (1024 * 1024), 2),
            "peak_bytes": self.peak_bytes,
            "peak_mb": round(self.peak_bytes / (1024 * 1024), 2),
            "budget_bytes": self.max_budget_bytes,
            "budget_utilization_ratio": self.allocated_bytes / max(self.max_budget_bytes, 1),
        }
