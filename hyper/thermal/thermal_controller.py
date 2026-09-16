"""
hyper/thermal/thermal_controller.py
===================================
HYPER Thermal Controller:
Tracks CPU package temperature, iGPU frequency, and sustained workload duration
to prevent thermal collapse on shared laptop cooling systems.
Supports profiling sustained runs (1 min, 5 min, 10 min, 30 min, 60 min).
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import psutil


@dataclass
class ThermalStatus:
    timestamp: float
    elapsed_seconds: float
    cpu_temp_celsius: float
    cpu_frequency_mhz: float
    is_throttling: bool
    recommended_lod_bias: float
    recommended_history_weight: float


class HyperThermalController:
    """
    Monitors thermal headroom and modulates temporal reconstruction weights
    and LOD bias to sustain steady frame rates without hitting thermal trip points.
    """

    def __init__(self, target_temp_ceiling: float = 85.0):
        self.ceiling = target_temp_ceiling
        self.start_time = time.perf_counter()
        self.history: List[ThermalStatus] = []

    def sample_thermal_state(self) -> ThermalStatus:
        now = time.perf_counter()
        elapsed = now - self.start_time

        # Attempt to read hardware temperatures
        temp_val = 65.0
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        temp_val = float(entries[0].current)
                        break
        except Exception:
            pass

        # CPU frequency
        freq_mhz = 2500.0
        try:
            freq = psutil.cpu_freq()
            if freq and freq.current:
                freq_mhz = float(freq.current)
        except Exception:
            pass

        is_throttling = temp_val >= self.ceiling

        # If throttling: increase temporal accumulation to 95% and bias LOD to reduce ALU heat
        if is_throttling:
            lod_bias = 1.5
            history_weight = 0.95
        elif temp_val > 75.0:
            lod_bias = 1.2
            history_weight = 0.90
        else:
            lod_bias = 1.0
            history_weight = 0.85

        status = ThermalStatus(
            timestamp=now,
            elapsed_seconds=round(elapsed, 2),
            cpu_temp_celsius=round(temp_val, 1),
            cpu_frequency_mhz=round(freq_mhz, 1),
            is_throttling=is_throttling,
            recommended_lod_bias=lod_bias,
            recommended_history_weight=history_weight,
        )
        self.history.append(status)
        return status
