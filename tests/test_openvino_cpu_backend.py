"""
tests/test_openvino_cpu_backend.py
==================================
Tests Phase 11 OPENVINO_CPU backend.
Verifies compiled execution on Intel CPU devices.
"""

import numpy as np
import pytest
from hyper.scheduler.heterogeneous_scheduler import HeterogeneousScheduler


def test_openvino_cpu_execution():
    sched = HeterogeneousScheduler()
    if not sched.has_openvino_cpu:
        pytest.skip("OpenVINO CPU device not available.")

    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    C_ov, timings = sched.execute_backend("OPENVINO_CPU", A, B)
    C_ref = A @ B

    assert np.allclose(C_ov, C_ref, atol=1e-4)
    assert timings["total_ms"] > 0
    assert timings["backend"] == "OPENVINO_CPU"
