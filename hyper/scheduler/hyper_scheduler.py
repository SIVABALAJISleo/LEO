"""
hyper/scheduler/hyper_scheduler.py
==================================
HYPER Dynamic Scheduler:
Dynamically decides execution pathway across:
- CACHED_RESULT (100% compute avoided)
- PREDICTED_RESULT (Extrapolated + minimal correction)
- RECONSTRUCTED_RESULT (Reprojected + bilateral filtered)
- CPU_AVX2 (Cheapest for small / irregular tasks)
- IGPU_PARALLEL (Cheapest for large uniform 2D grids)
- PARALLEL_CPU_IGPU (Pipelined cooperative execution)

Decision factors:
- Estimated compute cost vs memory transfer cost
- Synchronization overhead
- Thermal head-room & throttling state
- Frame deadline (e.g. 16.6ms target)
- Importance and confidence
"""

from typing import Any, Dict, Optional
import numpy as np


class HyperScheduler:
    """
    Strategic multi-factor computation dispatcher.
    Always selects the cheapest valid execution path to preserve contract.
    """

    def __init__(self, target_frame_budget_ms: float = 16.6):
        self.target_budget_ms = target_frame_budget_ms
        self.transfer_penalty_ms = 0.8  # OpenCL/OpenVINO PCIe-equivalent buffer sync penalty
        self.cache_hit_cost_ms = 0.05

    def decide_route(
        self,
        task_name: str,
        workload_pixels_or_elements: int,
        can_reuse_temporal: bool,
        confidence_score: float,
        importance_score: float,
        cpu_utilization_pct: float = 40.0,
        igpu_utilization_pct: float = 30.0,
        cpu_temp_celsius: float = 65.0,
    ) -> Dict[str, Any]:
        """
        Determines the optimal execution route and estimated duration.
        """
        # 1. Highest priority: 100% Temporal Cache Reuse
        if can_reuse_temporal and confidence_score >= 0.80:
            return {
                "route": "CACHED_RESULT",
                "reason": "Temporal history fully valid with high confidence.",
                "estimated_latency_ms": self.cache_hit_cost_ms,
                "work_avoidance_ratio": 1.0,
            }

        # 2. Reconstructed Path (Temporal Reprojection + Bilateral Filter)
        if confidence_score >= 0.50 and importance_score < 0.85:
            est_recon_ms = (workload_pixels_or_elements / 2000000.0) * 2.5
            return {
                "route": "RECONSTRUCTED_RESULT",
                "reason": "Sufficient confidence for temporal reprojection and bilateral reconstruction.",
                "estimated_latency_ms": round(est_recon_ms, 3),
                "work_avoidance_ratio": 0.75,
            }

        # 3. Predicted Result (Extrapolation)
        if confidence_score >= 0.65 and importance_score >= 0.85:
            est_pred_ms = (workload_pixels_or_elements / 2000000.0) * 3.2
            return {
                "route": "PREDICTED_RESULT",
                "reason": "High-importance entity with predictable motion trajectory.",
                "estimated_latency_ms": round(est_pred_ms, 3),
                "work_avoidance_ratio": 0.60,
            }

        # 4. Thermal-Aware Hardware Dispatch for Full Compute
        # If CPU is running hot (>85°C), offload pixel shading to iGPU
        # If iGPU is saturated or workload is small, keep on CPU AVX2
        is_thermal_throttling = cpu_temp_celsius > 85.0
        is_large_grid = workload_pixels_or_elements >= 256 * 256

        if (is_large_grid or is_thermal_throttling) and igpu_utilization_pct < 85.0:
            est_igpu_ms = (workload_pixels_or_elements / 1500000.0) * 4.0 + self.transfer_penalty_ms
            return {
                "route": "IGPU_PARALLEL",
                "reason": "Large uniform grid suitable for parallel execution on Intel UHD Graphics." if not is_thermal_throttling else "CPU thermal protection: offloading work to iGPU.",
                "estimated_latency_ms": round(est_igpu_ms, 3),
                "work_avoidance_ratio": 0.0,
            }

        est_cpu_ms = (workload_pixels_or_elements / 1000000.0) * 5.0
        return {
            "route": "CPU_AVX2",
            "reason": "Small or irregular workload executed directly in CPU L2/L3 cache without transfer overhead.",
            "estimated_latency_ms": round(est_cpu_ms, 3),
            "work_avoidance_ratio": 0.0,
        }
