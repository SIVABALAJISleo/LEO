#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/execution_fabric/telemetry.py
=====================================
Phase 13: Execution Fabric Telemetry.
Tracks real-time system metrics, kernel latencies, DRAM footprint,
and tail latency percentiles (P50, P90, P95, P99).
"""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
import numpy as np


class FabricTelemetry:
    """
    Records and calculates execution latency distributions and resource consumption.
    """

    def __init__(self):
        self.kernel_records: Dict[str, List[float]] = {}
        self.sample_timestamps: List[float] = []

    def record_kernel(self, kernel_name: str, latency_ms: float) -> None:
        if kernel_name not in self.kernel_records:
            self.kernel_records[kernel_name] = []
        self.kernel_records[kernel_name].append(latency_ms)
        self.sample_timestamps.append(time.perf_counter())

    def get_summary(self, kernel_name: Optional[str] = None) -> Dict[str, Any]:
        """Returns statistical distribution for kernel or all kernels."""
        if kernel_name:
            samples = self.kernel_records.get(kernel_name, [])
            return self._compute_percentiles(samples, kernel_name)

        # Aggregate across all
        all_samples = []
        for s in self.kernel_records.values():
            all_samples.extend(s)
        return self._compute_percentiles(all_samples, "aggregate")

    def _compute_percentiles(self, samples: List[float], label: str) -> Dict[str, Any]:
        if not samples:
            return {
                "label": label,
                "count": 0,
                "mean_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            }
        arr = np.array(samples, dtype=np.float64)
        return {
            "label": label,
            "count": len(samples),
            "mean_ms": round(float(np.mean(arr)), 4),
            "min_ms": round(float(np.min(arr)), 4),
            "max_ms": round(float(np.max(arr)), 4),
            "p50_ms": round(float(np.percentile(arr, 50)), 4),
            "p90_ms": round(float(np.percentile(arr, 90)), 4),
            "p95_ms": round(float(np.percentile(arr, 95)), 4),
            "p99_ms": round(float(np.percentile(arr, 99)), 4),
        }
