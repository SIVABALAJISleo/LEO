"""
tests/v8/test_v8_scheduler.py
=============================
Tests for HeterogeneousSchedulerV2 and DeviceCertificate.
"""

import numpy as np
import pytest

from hyper.v8.scheduler import HeterogeneousSchedulerV2, probe_hardware


def test_device_certificate_strict_constraints():
    cert = probe_hardware()
    assert cert.is_dgpu is False  # STRICT RULE: No discrete GPU
    assert cert.cpu_cores_physical >= 4
    assert cert.ram_gb >= 8.0


def test_scheduler_cpu_execution():
    scheduler = HeterogeneousSchedulerV2(enable_igpu=False)
    A = np.random.randn(16, 16).astype(np.float32)
    B = np.random.randn(16, 16).astype(np.float32)

    C, meta = scheduler.execute_gemm(A, B, force_backend="CPU")

    assert meta["backend"] == "CPU"
    assert np.allclose(C, A @ B, atol=1e-5)


def test_scheduler_auto_split():
    scheduler = HeterogeneousSchedulerV2(enable_igpu=True)
    ratio, reason = scheduler.compute_optimal_split(64, 64, 64)
    # Small problem should use 100% CPU
    assert ratio == 1.0
    assert "CPU" in reason
