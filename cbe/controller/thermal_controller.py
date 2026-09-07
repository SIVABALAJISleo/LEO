"""
cbe/controller/thermal_controller.py
Monitors thermal headroom, CPU/GPU clock frequencies, and power throttling.
Preemptively shifts work to cheaper precision and higher temporal reuse
before physical thermal throttling stalls the system.
"""

from __future__ import annotations

import psutil
from typing import Dict, Any, Optional


class ThermalController:
    """
    Supervises system thermals and power state.
    Triggers compute reduction to maintain thermal equilibrium on consumer laptops.
    """
    def __init__(self, target_cpu_util_max: float = 85.0):
        self.target_cpu_util_max = target_cpu_util_max
        self.thermal_state = "NOMINAL"  # NOMINAL, WARM, THROTTLING

    def check_thermal_state(self) -> Dict[str, Any]:
        cpu_util = psutil.cpu_percent(interval=None)
        
        freq = psutil.cpu_freq()
        current_freq_mhz = freq.current if freq else 2000.0
        max_freq_mhz = freq.max if (freq and freq.max > 0) else current_freq_mhz
        
        freq_ratio = current_freq_mhz / max(100.0, max_freq_mhz)
        
        # Throttling heuristic: high CPU utilization but frequency dropped below 60% of max
        is_throttled = (cpu_util > 80.0) and (freq_ratio < 0.60)
        is_warm = (cpu_util > 75.0) or (freq_ratio < 0.80)
        
        if is_throttled:
            self.thermal_state = "THROTTLING"
            mitigation_factor = 0.65  # Shed 35% of expensive computation
        elif is_warm:
            self.thermal_state = "WARM"
            mitigation_factor = 0.85  # Shed 15% of compute
        else:
            self.thermal_state = "NOMINAL"
            mitigation_factor = 1.00

        return {
            "thermal_state": self.thermal_state,
            "is_throttled": is_throttled,
            "cpu_util_pct": cpu_util,
            "current_freq_mhz": current_freq_mhz,
            "mitigation_factor": mitigation_factor,
            "recommended_actions": self._get_recommendations(is_throttled, is_warm)
        }

    def _get_recommendations(self, throttled: bool, warm: bool) -> List[str]:
        if throttled:
            return [
                "REDUCE_RENDER_RESOLUTION_TO_50",
                "INCREASE_TEMPORAL_REUSE_THRESHOLD",
                "FORCE_INT8_MODEL_INFERENCE",
                "SUPPRESS_DYNAMIC_LIGHTING_PASSES"
            ]
        elif warm:
            return [
                "USE_VRS_2X2_ON_BACKGROUND",
                "ENABLE_NEURAL_RECONSTRUCTION_OVER_NATIVE"
            ]
        return ["MAINTAIN_STANDARD_SCHEDULE"]
