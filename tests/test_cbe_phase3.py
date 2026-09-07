"""
tests/test_cbe_phase3.py
Unit tests for ResidualDetector, ResidualClassifier, ResidualScheduler, and ResidualRenderer.
"""

import numpy as np
import pytest

from cbe.residual.residual_detector import ResidualDetector
from cbe.residual.residual_classifier import ResidualClassifier, ResidualClass
from cbe.residual.residual_scheduler import ResidualScheduler
from cbe.residual.residual_renderer import ResidualRenderer


def test_residual_detector_exact():
    H, W = 64, 64
    target = np.ones((H, W, 3), dtype=np.float32)
    predicted = np.ones((H, W, 3), dtype=np.float32)
    
    # 10x10 patch changed in target
    target[10:20, 10:20] = 0.0
    
    detector = ResidualDetector(residual_threshold=0.05)
    metrics = detector.detect_exact(target, predicted)
    
    assert metrics.max_magnitude == 1.0
    assert metrics.spatial_density > 0.0
    assert metrics.spatial_density < 0.10  # 100 pixels out of 4096 = ~2.4%


def test_residual_classification_and_scheduling():
    H, W = 64, 64
    residual_map = np.zeros((H, W), dtype=np.float32)
    confidence_map = np.ones((H, W), dtype=np.float32)
    disocclusion_mask = np.zeros((H, W), dtype=bool)
    
    # Top-left quadrant has high residual & disocclusion
    residual_map[0:32, 0:32] = 0.8
    disocclusion_mask[0:32, 0:32] = True
    confidence_map[0:32, 0:32] = 0.0
    
    classifier = ResidualClassifier(tile_size=16)
    tiles = classifier.classify_tiles(residual_map, confidence_map, disocclusion_mask)
    
    # 64x64 with 16x16 tiles = 16 tiles total
    assert len(tiles) == 16
    
    # 4 tiles in top-left should be NOVEL, others UNCHANGED
    novel_count = sum(1 for t in tiles if t.residual_class == ResidualClass.NOVEL)
    unchanged_count = sum(1 for t in tiles if t.residual_class == ResidualClass.UNCHANGED)
    assert novel_count == 4
    assert unchanged_count == 12
    
    scheduler = ResidualScheduler()
    schedule = scheduler.schedule(tiles, height=H, width=W)
    
    assert len(schedule.fresh_tiles) == 4
    assert len(schedule.reused_tiles) == 12
    assert schedule.compute_elimination_ratio > 0.70  # ~75% compute eliminated


def test_residual_renderer_composition():
    H, W = 32, 32
    predicted = np.zeros((H, W, 3), dtype=np.float32)
    
    classifier = ResidualClassifier(tile_size=16)
    residual_map = np.zeros((H, W), dtype=np.float32)
    residual_map[0:16, 0:16] = 1.0  # Only tile (0,0) needs fresh render
    confidence_map = np.ones((H, W), dtype=np.float32)
    disocclusion_mask = np.zeros((H, W), dtype=bool)
    disocclusion_mask[0:16, 0:16] = True
    
    tiles = classifier.classify_tiles(residual_map, confidence_map, disocclusion_mask)
    scheduler = ResidualScheduler()
    schedule = scheduler.schedule(tiles, height=H, width=W)
    
    def mock_tile_render(x, y, w, h, scale):
        return np.ones((h, w, 3), dtype=np.float32) * 0.75
        
    renderer = ResidualRenderer()
    final_frame, stats = renderer.render_residual_frame(predicted, schedule, mock_tile_render)
    
    assert stats["computed_tiles"] == 1
    assert stats["reused_tiles"] == 3
    assert stats["tiles_saved_pct"] == 75.0
    
    # Top-left tile should have rendered value 0.75, other tiles should be 0.0
    assert np.allclose(final_frame[0:16, 0:16], 0.75)
    assert np.allclose(final_frame[16:32, 16:32], 0.0)
