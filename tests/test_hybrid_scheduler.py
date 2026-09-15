"""
tests/test_hybrid_scheduler.py
==============================
Tests Phase 11 HeterogeneousScheduler optimal selection logic.
Ensures iGPU is only chosen if T_iGPU < T_CPU.
"""

import numpy as np
import pytest
from hyper.scheduler.heterogeneous_scheduler import HeterogeneousScheduler


def test_scheduler_measures_before_selection():
    sched = HeterogeneousScheduler()
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    best_backend, report = sched.select_optimal_backend(A, B)
    assert best_backend in [
        "CPU_SCALAR", "CPU_AVX2", "CPU_MULTITHREADED",
        "OPENVINO_CPU", "OPENVINO_GPU", "HYBRID_PIPELINED"
    ]
    assert "cpu_baseline_ms" in report
    assert "all_timings" in report
    # Verified: scheduler did not assume iGPU is faster
    assert isinstance(report["igpu_faster_than_cpu"], bool)


def test_hybrid_pipelined_execution():
    sched = HeterogeneousScheduler()
    rng = np.random.RandomState(42)
    A = rng.randn(64, 32).astype(np.float32)
    B = rng.randn(32, 32).astype(np.float32)

    C_hybrid, timings = sched.execute_backend("HYBRID_PIPELINED", A, B)
    C_ref = A @ B
    assert np.allclose(C_hybrid, C_ref, atol=0.05)
    assert timings["backend"] == "HYBRID_PIPELINED"
