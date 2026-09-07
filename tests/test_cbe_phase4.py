"""
tests/test_cbe_phase4.py
Unit tests for PerceptualImportance, ImportanceMapEngine, AdaptiveResolutionController,
VariableRateShading, ComputeBudget, QualityController, and LatencyController.
"""

import numpy as np
import pytest

from cbe.importance.perceptual_importance import PerceptualImportance
from cbe.importance.importance_map import ImportanceMapEngine
from cbe.scheduling.adaptive_resolution import AdaptiveResolutionController
from cbe.scheduling.variable_rate import VariableRateShading, ShadingRate
from cbe.controller.compute_budget import ComputeBudget
from cbe.controller.quality_controller import QualityController, QualityContract
from cbe.controller.latency_controller import LatencyController


def test_perceptual_importance():
    H, W = 64, 64
    # Smooth image vs high-contrast edge
    smooth = np.ones((H, W, 3), dtype=np.float32) * 0.5
    edge = np.zeros((H, W, 3), dtype=np.float32)
    edge[:, 32:] = 1.0  # Sharp vertical edge down the center
    
    eng = PerceptualImportance()
    imp_smooth = eng.compute(smooth)
    imp_edge = eng.compute(edge)
    
    # Smooth areas should have low base importance (0.2)
    assert np.mean(imp_smooth) <= 0.25
    # Edge regions should have significantly higher importance
    assert np.max(imp_edge[:, 30:34]) >= 0.80


def test_adaptive_resolution_governor():
    gov = AdaptiveResolutionController(target_fps=60.0, hysteresis_frames=3)
    initial_scale = gov.get_current_scale()
    
    # Simulate heavy GPU load and long frame times (30ms > 16.6ms)
    for _ in range(5):
        gov.update(frame_time_ms=30.0, gpu_load=0.98)
        
    downscaled = gov.get_current_scale()
    assert downscaled < initial_scale
    
    w, h = gov.compute_internal_dimensions(1920, 1080)
    assert w < 1920
    assert h < 1080


def test_variable_rate_shading():
    vrs = VariableRateShading(tile_size=16)
    H, W = 64, 64
    importance = np.zeros((H, W), dtype=np.float32)
    # High importance in top-left tile only
    importance[0:16, 0:16] = 0.95
    
    rate_map, reduction_pct = vrs.generate_rate_map(importance)
    assert rate_map.shape == (4, 4)
    # Tile (0,0) should be RATE_1X1
    assert rate_map[0, 0] == int(ShadingRate.RATE_1X1)
    # Other tiles should be coarsened (RATE_4X4)
    assert rate_map[1, 1] == int(ShadingRate.RATE_4X4)
    assert reduction_pct > 70.0


def test_quality_controller_emergency_mode():
    contract = QualityContract(min_ssim=0.95, min_psnr=30.0)
    qc = QualityController(contract)
    
    # Passing quality
    rep = qc.evaluate_quality(current_ssim=0.98, current_psnr=35.0)
    assert rep["contract_passed"] is True
    assert rep["emergency_mode"] is False
    
    # Severe quality drop triggers emergency mode
    rep_bad = qc.evaluate_quality(current_ssim=0.82, current_psnr=22.0)
    assert rep_bad["contract_passed"] is False
    assert rep_bad["emergency_mode"] is True
    
    directives = qc.get_adjustment_directives()
    assert directives["force_native_resolution"] is True
    assert directives["disable_frame_prediction"] is True


def test_latency_controller():
    lc = LatencyController(target_display_fps=60.0, max_input_latency_ms=40.0)
    for _ in range(10):
        lc.record_frame(sim_duration_sec=0.002, render_duration_sec=0.010, input_latency_ms=18.0)
        
    rep = lc.get_report()
    assert rep.is_responsive is True
    assert rep.input_latency_ms == 18.0
    assert rep.render_fps > 0.0
