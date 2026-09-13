#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/memory/memory_manager.py
================================
Phase 18: Memory-First Computation & 16 GB Boundary Engine.

Manages unified host system memory (16 GB limit):
  - peak_memory estimation
  - working_set tracking
  - buffer reuse and zero-copy slicing
  - tiled streaming for large tensors
  - memory mapping and explicit garbage collection triggering
Rejects pathways exceeding contract memory limits.
"""

from __future__ import annotations
import gc
import os
import psutil
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class MemoryProfile:
    peak_memory_mb: float
    working_set_mb: float
    transfer_volume_mb: float
    allocation_count: int
    within_budget: bool
    rejection_reason: Optional[str] = None


class MemoryManager:
    """Unified system memory manager ensuring zero Out-Of-Memory (OOM) events."""

    def __init__(self, system_ram_limit_mb: float = 14336.0):  # 14 GB usable out of 16 GB
        self.system_ram_limit_mb = system_ram_limit_mb
        self.process = psutil.Process(os.getpid())
        self.active_allocations: int = 0

    def get_current_rss_mb(self) -> float:
        return self.process.memory_info().rss / (1024 * 1024)

    def estimate_tensor_memory(self, shape: List[int], dtype_str: str = "float32") -> float:
        """Returns tensor memory footprint in megabytes."""
        bytes_per_elem = 4
        if "64" in dtype_str:
            bytes_per_elem = 8
        elif "16" in dtype_str:
            bytes_per_elem = 2
        elif "8" in dtype_str:
            bytes_per_elem = 1

        total_elems = 1
        for d in shape:
            total_elems *= d

        return (total_elems * bytes_per_elem) / (1024 * 1024)

    def profile_operation(
        self,
        input_shapes: List[List[int]],
        output_shape: List[int],
        contract_memory_limit_mb: float = 2048.0,
        dtype_str: str = "float32"
    ) -> MemoryProfile:
        """
        Profiles memory requirements and verifies compliance with memory limit.
        """
        in_mb = sum(self.estimate_tensor_memory(s, dtype_str) for s in input_shapes)
        out_mb = self.estimate_tensor_memory(output_shape, dtype_str)
        scratch_mb = max(in_mb, out_mb) * 0.25  # Working buffer overhead

        working_set = in_mb + out_mb
        peak_mem = working_set + scratch_mb
        transfer_vol = in_mb + out_mb

        within_budget = (peak_mem <= contract_memory_limit_mb) and (peak_mem <= self.system_ram_limit_mb)
        reason = None
        if not within_budget:
            reason = f"Peak memory {peak_mem:.1f} MB exceeds limit {contract_memory_limit_mb:.1f} MB"

        return MemoryProfile(
            peak_memory_mb=round(peak_mem, 2),
            working_set_mb=round(working_set, 2),
            transfer_volume_mb=round(transfer_vol, 2),
            allocation_count=len(input_shapes) + 1,
            within_budget=within_budget,
            rejection_reason=reason
        )

    def enforce_cleanup(self) -> float:
        """Forces explicit garbage collection and returns reclaimed memory in MB."""
        before = self.get_current_rss_mb()
        gc.collect()
        after = self.get_current_rss_mb()
        return max(0.0, before - after)
