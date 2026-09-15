"""
tests/test_openvino_gpu_backend.py
==================================
Tests Phase 11 OPENVINO_GPU backend on Intel UHD integrated graphics.
Verifies execution, buffer management, and kernel/sync timing breakdown.
"""

import numpy as np
import pytest
from hyper.scheduler.heterogeneous_scheduler import HeterogeneousScheduler


def test_openvino_gpu_execution():
    sched = HeterogeneousScheduler()
    if not sched.has_openvino_gpu:
        pytest.skip("OpenVINO GPU (Intel UHD) device not available.")

    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    C_gpu, timings = sched.execute_backend("OPENVINO_GPU", A, B)
    C_ref = A @ B

    # Check numerical closeness
    assert np.allclose(C_gpu, C_ref, atol=0.05)
    assert timings["backend"] == "OPENVINO_GPU"
    assert "kernel_ms" in timings
    assert "sync_ms" in timings
    assert timings["total_ms"] > 0
