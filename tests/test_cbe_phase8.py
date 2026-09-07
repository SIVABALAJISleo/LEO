"""
tests/test_cbe_phase8.py
Unit tests for Phase 8: Core CBE Controller, Adaptive Multi-Fidelity Hierarchy,
Workload Optimization, and Intel-First Execution.
"""

import pytest
import numpy as np
import time

from cbe.controller import (
    CBEController,
    CBECycleResult,
    WorkloadController,
    ComputeBudget,
    QualityController,
    QualityContract,
    ThermalController,
    LatencyController,
    detect_hardware,
)
from render.multi_fidelity_renderer import MultiFidelityRenderer
from render.software_rt_pipeline import SoftwareRTPipeline
from render.fsr_upscaler import FSRUpscaler
from universal_compute_router.intel_optimal_execution import IntelOptimalExecution


def test_hardware_detection_and_budgeting():
    hw = detect_hardware()
    assert hw.physical_cores >= 4
    assert hw.logical_processors >= 4
    assert isinstance(hw.has_openvino_gpu, bool)

    budget = ComputeBudget(target_fps=60.0)
    budget.start_frame()
    budget.begin_stage("render")
    time.sleep(0.002)
    elapsed = budget.end_stage("render")
    assert elapsed > 0
    summary = budget.get_summary()
    assert summary["target_budget_ms"] > 16.0
    assert summary["budget_headroom_ms"] <= summary["target_budget_ms"]


def test_multi_fidelity_renderer_8_tiers():
    renderer = MultiFidelityRenderer(width=64, height=48)
    
    # Tier 7: Ground Truth
    t7_res = renderer.render(tier=7)
    assert t7_res["tier"] == MultiFidelityRenderer.TIER_7_GROUND_TRUTH
    assert t7_res["rays_fired"] == 64 * 48 * 32
    assert t7_res["latency_ms"] > 0
    assert t7_res["ssim"] == 1.0

    # Tier 0: Zero-Cost Cache Recall
    t0_res = renderer.render(tier=0)
    assert t0_res["tier"] == MultiFidelityRenderer.TIER_0_ZERO_COST_CACHE
    assert t0_res["rays_fired"] == 0
    assert t0_res["compute_elimination_ratio"] == 1.0

    # Tier 1: Reprojection Fill
    prev_frame = t7_res["frame"]
    t1_res = renderer.render(tier=1, prev_frame=prev_frame)
    assert t1_res["tier"] == MultiFidelityRenderer.TIER_1_REPROJECTION_FILL
    assert t1_res["rays_fired"] == 0
    assert t1_res["compute_elimination_ratio"] == 1.0
    assert t1_res["ssim"] > 0.8

    # Tier 3: Adaptive 50% Res + CAS
    t3_res = renderer.render(tier=3)
    assert t3_res["tier"] == MultiFidelityRenderer.TIER_3_ADAPTIVE_RESTIR_CAS
    assert t3_res["rays_fired"] < t7_res["rays_fired"]
    assert t3_res["compute_elimination_ratio"] > 0.5


def test_software_rt_pipeline():
    pipeline = SoftwareRTPipeline(target_width=64, target_height=48, preview_spp=2)
    result = pipeline.render_frame()
    assert "frame" in result
    assert result["frame"].shape == (48, 64, 3)
    assert result["total_latency_ms"] > 0
    assert result["actual_rays_fired_pct"] < 25.0


def test_fsr_upscaler_and_intel_optimal():
    upscaler = FSRUpscaler(scale_factor=2.0)
    low_res = np.ones((24, 32, 3), dtype=np.float32) * 0.5
    high_res = upscaler.upscale(low_res)
    assert high_res.shape == (48, 64, 3)

    intel_exec = IntelOptimalExecution()
    x = np.random.randn(2, 16).astype(np.float32)
    W = np.random.randn(16, 32).astype(np.float32)
    b = np.zeros((32,), dtype=np.float32)
    out = intel_exec.execute_fused_kernel(x, W, b)
    assert out.shape == (2, 32)
    # Check LayerNorm properties: zero mean, unit variance
    np.testing.assert_allclose(np.mean(out, axis=-1), 0.0, atol=1e-5)
    np.testing.assert_allclose(np.var(out, axis=-1), 1.0, atol=1e-3)


def test_cbe_controller_cycle():
    contract = QualityContract(target_fps=60.0, min_ssim=0.85)
    controller = CBEController(contract=contract)
    
    # Run consecutive cycles
    frame0 = np.random.uniform(0.2, 0.8, (48, 64, 3)).astype(np.float32)
    res0 = controller.process_frame(current_frame=frame0, motion_level=0.5)
    assert isinstance(res0, CBECycleResult)
    assert res0.compute_elimination_ratio >= 0.0
    assert res0.total_latency_ms > 0

    # Static frame should achieve high elimination ratio
    res1 = controller.process_frame(current_frame=frame0, motion_level=0.0)
    assert res1.compute_elimination_ratio >= 0.40
