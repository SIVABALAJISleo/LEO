"""
cbe/prediction/motion_predictor.py
Kinematic and Kalman-style motion extrapolation for camera and dynamic entities.
Extrapolates trajectories across subpixel intervals to compute predictive motion fields.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple, Optional


class MotionPredictor:
    """
    Extrapolates 2nd-order kinematic trajectories (velocity + acceleration)
    to predict where camera and objects will be in frame N+1.
    """
    def __init__(self, history_len: int = 4):
        self.history_len = history_len
        self.pos_history: List[np.ndarray] = []
        self.time_history: List[float] = []

    def push_sample(self, position: np.ndarray, timestamp: float):
        self.pos_history.append(np.asarray(position, dtype=np.float32))
        self.time_history.append(timestamp)
        if len(self.pos_history) > self.history_len:
            self.pos_history.pop(0)
            self.time_history.pop(0)

    def predict_next_position(self, delta_time: float = 0.01667) -> np.ndarray:
        """
        Extrapolates position at timestamp = current + delta_time.
        """
        n = len(self.pos_history)
        if n == 0:
            return np.zeros(3, dtype=np.float32)
        if n == 1:
            return self.pos_history[0].copy()
            
        # 1st-order velocity
        dt1 = max(1e-4, self.time_history[-1] - self.time_history[-2])
        v1 = (self.pos_history[-1] - self.pos_history[-2]) / dt1
        
        if n >= 3:
            # 2nd-order acceleration
            dt0 = max(1e-4, self.time_history[-2] - self.time_history[-3])
            v0 = (self.pos_history[-2] - self.pos_history[-3]) / dt0
            accel = (v1 - v0) / ((dt1 + dt0) * 0.5)
            # Clamped acceleration to prevent divergence on jerky inputs
            accel = np.clip(accel, -50.0, 50.0)
            pred = self.pos_history[-1] + v1 * delta_time + 0.5 * accel * (delta_time ** 2)
        else:
            pred = self.pos_history[-1] + v1 * delta_time
            
        return pred.astype(np.float32)
