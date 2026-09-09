"""
tests/test_hostile_graphics.py
==============================
Hostile Self-Falsification Suite: Camera Teleportation & Scene Cuts.

Verifies:
  - Sudden 100% camera teleportation / cut (disoccluding the entire screen)
    is detected by the residual detector and triggers full tile recomputation.
  - Perceptual quality contract (PSNR >= 35.0 dB, SSIM >= 0.95) is strictly maintained.
"""

import pytest
import numpy as np
from hyper_cco.temporal_graphics import TemporalGraphicsEngine


def test_scene_cut_full_recompute_defense():
    """A sudden scene cut must trigger full tile recomputation without visual artifacts."""
    engine = TemporalGraphicsEngine(history_buffer_size=4)
    H, W = 128, 128

    # Frame 1: Scene A (all dark)
    frame_a = np.zeros((H, W, 3), dtype=np.float32)
    engine.push_history(frame_a)

    # Frame 2: Scene B (all bright procedural texture, 100% cut)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    frame_b = (0.5 + 0.5 * np.sin(xx / 10.0)).repeat(3).reshape(H, W, 3)

    # Execute temporal reconstruction with hostile cut
    res = engine.execute_temporal_reconstruction(
        render_low_res_fn=lambda: np.zeros((32, 32, 3), dtype=np.float32),
        render_exact_tile_fn=lambda y, ye, x, xe: frame_b[y:ye, x:xe],
        ground_truth_for_audit=frame_b,
        motion_vectors=None,  # No valid motion vector during cut
        target_shape=(H, W),
        tile_size=16,
        residual_threshold=0.01,
        min_psnr=30.0,
        min_ssim=0.90,
    )

    # All tiles should be marked dirty and recomputed
    assert res.recomputed_tile_ratio > 0.80
    assert res.contract_satisfied is True
    assert res.psnr_db >= 30.0
    assert res.ssim >= 0.90
