"""
hyper_x/ahce/telemetry.py
========================
Host resource telemetry for AHCE.
"""

from __future__ import annotations
import time
import psutil
from typing import Dict, Any
from .evidence import AHCETelemetryRecord


class AHCETelemetryCollector:
    """Samples real system telemetry from the Intel Core i5 substrate."""

    def sample(self, latency_ms: float = 0.0) -> AHCETelemetryRecord:
        cpu_load = float(psutil.cpu_percent(interval=None))
        mem_info = psutil.virtual_memory()
        used_mb = float(mem_info.used / (1024 * 1024))

        return AHCETelemetryRecord(
            latency_ms=round(latency_ms, 3),
            cpu_utilization_pct=round(cpu_load, 1),
            ram_used_mb=round(used_mb, 1),
            cache_hits=0,
            cache_misses=0,
            work_steals=0
        )
