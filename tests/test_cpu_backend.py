"""
tests/test_cpu_backend.py
=========================
Tests Phase 11 CPU backends: CPU_SCALAR, CPU_AVX2, and CPU_MULTITHREADED.
Verifies correct numerical results and latency tracking.
"""

import numpy as np
import pytest
from hyper.scheduler.heterogeneous_scheduler import HeterogeneousScheduler


def test_cpu_backends_numerical_consistency():
    sched = HeterogeneousScheduler()
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    c_scalar, t_scalar = sched.execute_backend("CPU_SCALAR", A, B)
    c_avx2, t_avx2 = sched.execute_backend("CPU_AVX2", A, B)
    c_multi, t_multi = sched.execute_backend("CPU_MULTITHREADED", A, B)

    # Numerical consistency
    assert np.allclose(c_scalar, c_avx2, atol=1e-5)
    assert np.allclose(c_avx2, c_multi, atol=1e-5)

    # Timing metrics reported
    assert t_scalar["total_ms"] > 0
    assert t_avx2["total_ms"] > 0
    assert t_multi["total_ms"] > 0
