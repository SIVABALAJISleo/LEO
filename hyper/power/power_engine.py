"""
hyper/power/power_engine.py
===========================
Power-Aware Engine (Section 35):
Estimates package power (TDP), energy per operation, and performance-per-watt.
"""

import time
import psutil
from typing import Dict, Any


class PowerEngine:
    """
    Estimates processor package energy and efficiency.
    """
    def __init__(self, tdp_watts: float = 45.0):
        self.tdp_watts = tdp_watts # Core i5-12450H Base TDP 45W, Max Turbo 95W

    def estimate_energy_joules(self, elapsed_ms: float, cpu_utilization_pct: float) -> Dict[str, Any]:
        power_draw_watts = 15.0 + (self.tdp_watts - 15.0) * (cpu_utilization_pct / 100.0)
        energy_joules = power_draw_watts * (elapsed_ms / 1000.0)

        return {
            "estimated_power_draw_watts": round(power_draw_watts, 2),
            "estimated_energy_joules": round(energy_joules, 4),
            "elapsed_ms": round(elapsed_ms, 3)
        }
