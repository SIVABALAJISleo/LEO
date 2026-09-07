"""
cbe/prediction/workload_predictor.py
Predicts upcoming computational demand and required shading resolution.
Forecasts compute spikes from fast camera rotations or mass disocclusions.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any


class WorkloadPredictor:
    """
    Analyzes motion velocity and scene change rate to forecast upcoming frame compute cost.
    """
    def __init__(self):
        self.workload_history: List[float] = []

    def predict_demand(
        self,
        camera_angular_velocity_deg_s: float,
        disocclusion_ratio: float,
        active_object_count: int
    ) -> Dict[str, Any]:
        """
        Computes predicted workload index [0.0 = minimal, 1.0 = extreme load].
        """
        # Angular velocity factor (rapid turns cause large disocclusion cascades)
        rot_factor = min(1.0, camera_angular_velocity_deg_s / 90.0)
        disocc_factor = min(1.0, disocclusion_ratio * 3.0)
        obj_factor = min(1.0, active_object_count / 100.0)
        
        predicted_demand = 0.40 * rot_factor + 0.40 * disocc_factor + 0.20 * obj_factor
        
        # Recommendation
        if predicted_demand > 0.70:
            rec_resolution_scale = 0.50
            rec_strategy = "AGGRESSIVE_SPARSE_RECONSTRUCT"
        elif predicted_demand > 0.40:
            rec_resolution_scale = 0.75
            rec_strategy = "BALANCED_TEMPORAL_RECONSTRUCT"
        else:
            rec_resolution_scale = 1.00
            rec_strategy = "TEMPORAL_REUSE_NATIVE"
            
        return {
            "predicted_demand_score": round(predicted_demand, 3),
            "recommended_scale": rec_resolution_scale,
            "recommended_strategy": rec_strategy
        }
