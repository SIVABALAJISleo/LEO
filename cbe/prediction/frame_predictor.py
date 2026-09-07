"""
cbe/prediction/frame_predictor.py
Frame prediction and predictive precomputation engine.
Prepares camera transforms, visibility sets, and residual estimates for frame N+1
while frame N is presenting on screen.
"""

from __future__ import annotations

import time
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional

from cbe.state.scene_state import SceneState, CameraState
from .motion_predictor import MotionPredictor
from .visibility_predictor import VisibilityPredictor
from .lighting_predictor import LightingPredictor
from .workload_predictor import WorkloadPredictor


@dataclass
class PredictedFrameState:
    predicted_camera: CameraState
    predicted_position: np.ndarray
    predicted_demand: Dict[str, Any]
    predicted_delta_time: float


class FramePredictor:
    """
    Lightweight future frame predictor running concurrently with frame display.
    """
    def __init__(self):
        self.cam_motion = MotionPredictor()
        self.visibility = VisibilityPredictor()
        self.lighting = LightingPredictor()
        self.workload = WorkloadPredictor()

    def update_history(self, current_scene: SceneState):
        self.cam_motion.push_sample(current_scene.camera.position, current_scene.timestamp)
        if current_scene.lights:
            first_light = next(iter(current_scene.lights.values()))
            self.lighting.update(first_light.intensity)

    def predict_next_frame(
        self,
        current_scene: SceneState,
        delta_time: float = 0.01667
    ) -> PredictedFrameState:
        """
        Synthesizes predictive state for frame N+1.
        """
        # 1. Extrapolate camera position
        pred_pos = self.cam_motion.predict_next_position(delta_time)
        
        # Build predicted camera
        pred_cam = CameraState(
            position=pred_pos,
            target=current_scene.camera.target + (pred_pos - current_scene.camera.position),
            up=current_scene.camera.up.copy(),
            fov_degrees=current_scene.camera.fov_degrees,
            aspect_ratio=current_scene.camera.aspect_ratio
        )
        
        # 2. Estimate angular velocity
        cam_dir_curr = current_scene.camera.target - current_scene.camera.position
        cam_dir_pred = pred_cam.target - pred_cam.position
        
        d_curr_norm = cam_dir_curr / max(1e-5, np.linalg.norm(cam_dir_curr))
        d_pred_norm = cam_dir_pred / max(1e-5, np.linalg.norm(cam_dir_pred))
        
        cos_angle = float(np.clip(np.dot(d_curr_norm, d_pred_norm), -1.0, 1.0))
        angle_deg = np.degrees(np.arccos(cos_angle))
        ang_velocity = angle_deg / max(1e-4, delta_time)
        
        # 3. Predict workload demand
        demand = self.workload.predict_demand(
            camera_angular_velocity_deg_s=ang_velocity,
            disocclusion_ratio=0.05,
            active_object_count=len(current_scene.objects)
        )
        
        return PredictedFrameState(
            predicted_camera=pred_cam,
            predicted_position=pred_pos,
            predicted_demand=demand,
            predicted_delta_time=delta_time
        )
