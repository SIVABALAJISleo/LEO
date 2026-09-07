"""
cbe/telemetry/hardware_metrics.py
=============================================================================
System Hardware Metrics & Host Telemetry
=============================================================================
Live polling of CPU core states, RAM utilization, and Intel execution device status.
"""

from __future__ import annotations

import psutil
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class HardwareSample:
    timestamp: float
    cpu_percent_total: float
    cpu_freq_current_mhz: float
    cpu_freq_max_mhz: float
    ram_used_gb: float
    ram_percent: float
    is_throttled: bool


class HardwareMetrics:
    """
    Monitors live CPU/GPU hardware health and resource saturation.
    """

    def __init__(self):
        self.samples: List[HardwareSample] = []

    def sample(self) -> HardwareSample:
        import time
        t = time.time()
        cpu_tot = psutil.cpu_percent(interval=None)
        
        freq = psutil.cpu_freq()
        cur_freq = freq.current if freq else 2000.0
        max_freq = freq.max if (freq and freq.max > 0) else cur_freq

        mem = psutil.virtual_memory()
        used_gb = (mem.total - mem.available) / (1024**3)
        pct = mem.percent

        freq_ratio = cur_freq / max(100.0, max_freq)
        is_throttled = (cpu_tot > 80.0) and (freq_ratio < 0.60)

        s = HardwareSample(
            timestamp=t,
            cpu_percent_total=cpu_tot,
            cpu_freq_current_mhz=cur_freq,
            cpu_freq_max_mhz=max_freq,
            ram_used_gb=round(used_gb, 2),
            ram_percent=pct,
            is_throttled=is_throttled,
        )
        self.samples.append(s)
        return s

    def get_summary(self) -> Dict[str, Any]:
        if not self.samples:
            return {"samples_count": 0}
        cpus = [s.cpu_percent_total for s in self.samples]
        return {
            "samples_count": len(self.samples),
            "avg_cpu_percent": round(float(sum(cpus) / len(cpus)), 1),
            "max_cpu_percent": round(float(max(cpus)), 1),
            "throttled_events": sum(1 for s in self.samples if s.is_throttled),
        }
