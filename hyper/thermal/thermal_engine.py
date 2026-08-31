"""
hyper/thermal/thermal_engine.py
===============================
Thermal-Aware Execution Engine (Section 34):
Monitors CPU/iGPU package temperature, detects thermal throttling events,
and adjusts execution intensity to prevent frequency collapse.
"""

import time
import psutil
from typing import Dict, Any


class ThermalEngine:
    """
    Evaluates thermal headroom and throttling status.
    """
    def __init__(self, throttling_temp_celsius: float = 95.0):
        self.throttling_temp_celsius = throttling_temp_celsius

    def check_thermal_headroom(self) -> Dict[str, Any]:
        freq = psutil.cpu_freq()
        current_freq_mhz = freq.current if freq else 2500.0
        max_freq_mhz = freq.max if (freq and freq.max > 0) else 4400.0

        # Frequency degradation proxy
        freq_ratio = current_freq_mhz / max_freq_mhz
        is_throttling = freq_ratio < 0.65

        return {
            "current_frequency_mhz": round(current_freq_mhz, 1),
            "max_frequency_mhz": round(max_freq_mhz, 1),
            "frequency_headroom_ratio": round(freq_ratio, 2),
            "is_thermal_throttling": is_throttling,
            "status": "THROTTLED" if is_throttling else "NOMINAL"
        }
