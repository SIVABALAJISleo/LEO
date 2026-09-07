"""
cbe/telemetry/power_metrics.py
=============================================================================
Power & Energy Efficiency Telemetry
=============================================================================
Calculates estimated Watts, Joules-per-frame, and energy reduction ratio (ERR).
Relates compute elimination directly to battery life preservation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class PowerSample:
    frame_index: int
    estimated_watts: float
    joules_spent: float
    baseline_joules: float
    energy_reduction_ratio: float


class PowerMetrics:
    """
    Estimates package energy expenditure based on measured active time and TDP envelope.
    For Intel Core i5-13420H, Base TDP is ~45W, Turbo up to 95W, Idle ~10W.
    """

    def __init__(self, tdp_watts: float = 45.0, idle_watts: float = 10.0):
        self.tdp_watts = tdp_watts
        self.idle_watts = idle_watts
        self.samples: List[PowerSample] = []

    def evaluate_frame_energy(
        self,
        frame_index: int,
        active_latency_ms: float,
        baseline_latency_ms: float,
        cpu_load_factor: float = 0.8
    ) -> PowerSample:
        """
        Calculates Joules = Power(W) * Time(s).
        """
        # Estimated power during active execution
        estimated_w = self.idle_watts + (self.tdp_watts - self.idle_watts) * cpu_load_factor
        
        # Joules = Watts * seconds
        actual_joules = estimated_w * (active_latency_ms / 1000.0)
        baseline_joules = estimated_w * (baseline_latency_ms / 1000.0)
        
        err = 0.0
        if baseline_joules > 1e-6:
            err = max(0.0, 1.0 - (actual_joules / baseline_joules))

        sample = PowerSample(
            frame_index=frame_index,
            estimated_watts=round(estimated_w, 2),
            joules_spent=round(actual_joules, 4),
            baseline_joules=round(baseline_joules, 4),
            energy_reduction_ratio=round(err, 4),
        )
        self.samples.append(sample)
        return sample

    def get_summary(self) -> Dict[str, Any]:
        if not self.samples:
            return {"total_frames": 0, "cumulative_joules_saved": 0.0}

        total_actual = sum(s.joules_spent for s in self.samples)
        total_baseline = sum(s.baseline_joules for s in self.samples)
        saved = max(0.0, total_baseline - total_actual)
        overall_err = 1.0 - (total_actual / max(1e-6, total_baseline))

        return {
            "total_frames": len(self.samples),
            "total_joules_actual": round(total_actual, 3),
            "total_joules_baseline": round(total_baseline, 3),
            "cumulative_joules_saved": round(saved, 3),
            "energy_reduction_ratio": round(overall_err, 4),
        }
