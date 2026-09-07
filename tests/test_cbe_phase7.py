"""
tests/test_cbe_phase7.py
Unit tests for MotionPredictor, VisibilityPredictor, WorkloadPredictor,
FramePredictor, and upgraded EarlyExitRouter.
"""

import numpy as np
import pytest

from cbe.state.scene_state import SceneState, CameraState
from cbe.prediction.motion_predictor import MotionPredictor
from cbe.prediction.visibility_predictor import VisibilityPredictor
from cbe.prediction.workload_predictor import WorkloadPredictor
from cbe.prediction.frame_predictor import FramePredictor
from bypass.leo_early_exit_router import EarlyExitRouter


def test_motion_predictor_kinematics():
    mp = MotionPredictor()
    # Linear movement along X at 10 units/sec
    mp.push_sample(np.array([0.0, 0.0, 0.0]), timestamp=0.0)
    mp.push_sample(np.array([1.0, 0.0, 0.0]), timestamp=0.1)
    mp.push_sample(np.array([2.0, 0.0, 0.0]), timestamp=0.2)
    
    # Predict at t = 0.3 (+0.1s)
    pred_pos = mp.predict_next_position(delta_time=0.1)
    assert np.isclose(pred_pos[0], 3.0, atol=0.1)
    assert np.isclose(pred_pos[1], 0.0)


def test_visibility_frustum_culling():
    vp = VisibilityPredictor()
    cam = CameraState(position=np.array([0, 0, -5], dtype=np.float32), target=np.array([0, 0, 0], dtype=np.float32))
    cam.update_matrices()
    
    # Object directly in front of camera
    box_visible_min = np.array([-1, -1, 0], dtype=np.float32)
    box_visible_max = np.array([1, 1, 2], dtype=np.float32)
    assert vp.is_box_visible(box_visible_min, box_visible_max, cam.view_proj_matrix) is True
    
    # Object completely behind camera
    box_behind_min = np.array([-1, -1, -20], dtype=np.float32)
    box_behind_max = np.array([1, 1, -10], dtype=np.float32)
    assert vp.is_box_visible(box_behind_min, box_behind_max, cam.view_proj_matrix) is False


def test_workload_predictor():
    wp = WorkloadPredictor()
    # High turn speed (120 deg/s) + high disocclusion
    high_load = wp.predict_demand(camera_angular_velocity_deg_s=120.0, disocclusion_ratio=0.35, active_object_count=50)
    assert high_load["predicted_demand_score"] > 0.60
    assert high_load["recommended_scale"] <= 0.75
    
    # Static view
    low_load = wp.predict_demand(camera_angular_velocity_deg_s=0.0, disocclusion_ratio=0.01, active_object_count=10)
    assert low_load["predicted_demand_score"] < 0.30
    assert low_load["recommended_scale"] == 1.00


def test_frame_predictor():
    fp = FramePredictor()
    scene = SceneState()
    scene.camera.position = np.array([0, 0, 0], dtype=np.float32)
    scene.camera.target = np.array([0, 0, 5], dtype=np.float32)
    scene.timestamp = 1.0
    fp.update_history(scene)
    
    # Second frame shifted along Z
    scene2 = SceneState()
    scene2.camera.position = np.array([0, 0, 1], dtype=np.float32)
    scene2.camera.target = np.array([0, 0, 6], dtype=np.float32)
    scene2.timestamp = 1.01667
    fp.update_history(scene2)
    
    pred_state = fp.predict_next_frame(scene2, delta_time=0.01667)
    assert pred_state.predicted_position[2] > 1.0
    assert "recommended_scale" in pred_state.predicted_demand


def test_early_exit_router_calibrated():
    router = EarlyExitRouter(confidence_threshold=0.80, max_entropy=0.30)
    
    # 1. Decisive one-hot vector (low entropy, high margin) -> should early exit
    decisive_logits = np.zeros(256, dtype=np.float32)
    decisive_logits[10] = 50.0  # Dominant logit
    exit_early, out = router.evaluate_intermediate_state(decisive_logits)
    assert exit_early is True
    assert out is not None
    
    # 2. Uniform / high entropy vector -> should continue to full model
    uniform_logits = np.ones(256, dtype=np.float32)
    exit_early_uni, out_uni = router.evaluate_intermediate_state(uniform_logits)
    assert exit_early_uni is False
    assert out_uni is None
