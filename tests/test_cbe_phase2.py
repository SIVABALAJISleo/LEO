"""
tests/test_cbe_phase2.py
Tests for SceneState, ObjectState, StateMemoryPool, and TemporalReuseEngine.
"""

import numpy as np
import pytest

from cbe.state.scene_state import SceneState, CameraState, LightState
from cbe.state.object_state import ObjectState
from cbe.state.temporal_state import TemporalStateBuffer, TemporalFrameRecord
from cbe.state.state_memory import StateMemoryPool
from cbe.reuse.temporal_reuse import TemporalReuseEngine


def test_object_state_hashing():
    obj1 = ObjectState(object_id="cube_1", position=np.array([1.0, 2.0, 3.0]))
    hash1 = obj1.state_hash
    assert len(hash1) == 16  # 8 bytes hex
    
    # Static clone should produce identical hash
    obj2 = ObjectState(object_id="cube_1", position=np.array([1.0, 2.0, 3.0]))
    assert obj1.state_hash == obj2.state_hash
    
    # Moving object changes hash
    obj1.update_transform(np.array([1.0, 2.5, 3.0]))
    assert obj1.state_hash != hash1


def test_scene_state_diff():
    scene = SceneState()
    obj1 = ObjectState(object_id="cube_1", position=np.array([0, 0, 0]))
    scene.add_object(obj1)
    
    # Clone for previous state
    scene_prev = SceneState(camera=CameraState())
    scene_prev.add_object(ObjectState(object_id="cube_1", position=np.array([0, 0, 0])))
    
    # Identical scenes should recognize exact reuse
    diff_res = scene.diff(scene_prev)
    assert diff_res["strategy_hint"] == "EXACT_REUSE"
    assert diff_res["bypass_possible"] is True
    
    # Camera motion should trigger temporal reprojection
    scene.camera.position += np.array([0.5, 0.0, 0.0])
    scene.camera.update_matrices()
    scene.compute_scene_hash()
    
    diff_moved = scene.diff(scene_prev)
    assert diff_moved["camera_moved"] is True
    assert diff_moved["strategy_hint"] == "TEMPORAL_REPROJECTION"


def test_state_memory_pool():
    pool = StateMemoryPool(max_cached_per_shape=4)
    buf1 = pool.acquire((120, 160, 3), dtype=np.float32)
    assert buf1.shape == (120, 160, 3)
    
    pool.release(buf1)
    buf2 = pool.acquire((120, 160, 3), dtype=np.float32)
    # buf2 should come from pool hit
    stats = pool.stats()
    assert stats["pool_hits"] == 1


def test_temporal_reuse_reprojection():
    engine = TemporalReuseEngine()
    H, W = 64, 64
    
    # Create a synthetic image with a gradient
    y, x = np.mgrid[0:H, 0:W]
    prev_color = np.stack([x / W, y / H, np.zeros_like(x)], axis=-1).astype(np.float32)
    prev_depth = np.ones((H, W), dtype=np.float32) * 5.0
    current_depth = np.ones((H, W), dtype=np.float32) * 5.0
    
    # Uniform 2-pixel rightward motion (dx=2, dy=0)
    motion_vectors = np.zeros((H, W, 2), dtype=np.float32)
    motion_vectors[..., 0] = 2.0
    
    res = engine.evaluate_temporal_reuse(
        prev_color=prev_color,
        prev_depth=prev_depth,
        current_depth=current_depth,
        motion_vectors=motion_vectors
    )
    
    assert res.reusable_pixel_ratio > 0.90
    assert res.avg_confidence > 0.85
    assert res.reprojected_color.shape == (H, W, 3)
    
    # Test disocclusion detection
    current_depth[20:40, 20:40] = 10.0  # sudden depth leap
    res_disoccluded = engine.evaluate_temporal_reuse(
        prev_color=prev_color,
        prev_depth=prev_depth,
        current_depth=current_depth,
        motion_vectors=motion_vectors
    )
    assert np.any(res_disoccluded.disocclusion_mask)
    assert res_disoccluded.reusable_pixel_ratio < res.reusable_pixel_ratio
