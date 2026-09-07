"""
tests/test_cbe_phase9.py
Unit tests for Phase 9: Telemetry & Adversarial Validation.
Verifies mathematically sound CER, PHI hashing, visual quality metrics,
power/energy tracking, correctness invariants, and adversarial stress testing.
"""

import pytest
import numpy as np

from cbe.telemetry import (
    ComputeMetrics,
    QualityMetrics,
    HardwareMetrics,
    PowerMetrics,
)
from cbe.validation import (
    CorrectnessValidator,
    VisualQualityValidator,
    RegressionAuditor,
    AdversarialStressTester,
)


def test_compute_metrics_cer_and_phi():
    metrics = ComputeMetrics()
    
    # 50% rays, 40% latency -> CER must strictly follow formula with no double-counting
    sample = metrics.record_frame(
        frame_index=1,
        baseline_rays=10000,
        actual_rays=5000,
        baseline_latency_ms=16.67,
        actual_latency_ms=6.67,
        overhead_latency_ms=1.0,
    )
    assert sample.ray_cer == 0.50
    assert sample.net_cer > 0.40  # (16.67 - 7.67) / 16.67 ~ 0.54
    assert 0.0 <= sample.net_cer <= 1.0

    # PHI hash test
    frame1 = np.ones((64, 64, 3), dtype=np.float32) * 0.5
    frame2 = np.ones((64, 64, 3), dtype=np.float32) * 0.5
    assert metrics.compute_phi(frame1) == metrics.compute_phi(frame2)


def test_quality_metrics_and_flicker():
    qm = QualityMetrics(ssim_min=0.90, psnr_min=25.0)
    
    y, x = np.mgrid[0:32, 0:32].astype(np.float32)
    ref = (x + y) / 64.0
    ref = np.stack([ref, ref, ref], axis=-1)
    noisy = ref + np.random.normal(0, 0.01, ref.shape).astype(np.float32)
    noisy = np.clip(noisy, 0.0, 1.0)

    sample = qm.evaluate_frame(frame_index=1, reconstructed=noisy, ground_truth=ref)
    assert sample.ssim > 0.85
    assert sample.psnr > 25.0
    assert sample.temporal_flicker >= 0.0


def test_hardware_and_power_telemetry():
    hw = HardwareMetrics()
    sample = hw.sample()
    assert sample.ram_percent > 0
    assert sample.cpu_percent_total >= 0

    power = PowerMetrics(tdp_watts=45.0, idle_watts=10.0)
    p_sample = power.evaluate_frame_energy(
        frame_index=1, active_latency_ms=5.0, baseline_latency_ms=16.67
    )
    assert p_sample.joules_spent < p_sample.baseline_joules
    assert p_sample.energy_reduction_ratio > 0.5


def test_correctness_validator():
    validator = CorrectnessValidator()
    checks = validator.run_all_checks()
    assert checks["hash_determinism"] is True
    assert checks["dag_propagation"] is True
    assert checks["buffer_finite_check"] is True


def test_adversarial_stress_suite():
    tester = AdversarialStressTester(target_fps=60.0)
    
    # Run camera teleport test
    report_teleport = tester.test_camera_teleportation(num_frames=8)
    assert report_teleport.no_crash_or_nan is True
    assert report_teleport.p99_latency_ms > 0
    assert report_teleport.min_ssim > 0.70

    # Run strobe lighting test
    report_strobe = tester.test_strobe_lighting(num_frames=8)
    assert report_strobe.no_crash_or_nan is True
    assert report_strobe.passed is True
