"""
tests/hyper_escape/test_scheduler.py
Validates Universal CPU/iGPU Adaptive Scheduler (Feature F / Section 8).
Tests backend selection policy, transfer overhead accounting, safe CPU fallback,
and execution routing.
"""
import pytest
import numpy as np

from hyper_universal.contracts.contract_engine import ContractRegistry
from hyper_universal.backends.registry import BackendCapabilityRegistry
from hyper_universal.scheduler.scheduler import UniversalScheduler


def test_scheduler_initialization():
    scheduler = UniversalScheduler()
    assert scheduler.backend_registry is not None
    assert scheduler.contract_registry is not None


def test_scheduler_select_backend_for_gemm():
    scheduler = UniversalScheduler()
    # For large dense GEMM, should select CPU_AVX2 (or OPENCL_IGPU if available)
    plan = scheduler.schedule_workload("dense_gemm_512x512")
    assert plan.workload_id == "dense_gemm_512x512"
    assert plan.selected_backend in ["CPU_AVX2", "OPENCL_IGPU"]
    assert plan.fallback_backend == "CPU_AVX2"


def test_scheduler_execute_with_fallback():
    scheduler = UniversalScheduler()

    # Function that succeeds on fallback
    def failing_fn(x):
        raise RuntimeError("Simulated OpenCL launch crash")

    def fallback_fn(x):
        return x * 2.0

    x = np.array([1.0, 2.0, 3.0], dtype=np.float32)

    # Calling execute_with_fallback should catch the crash, invoke fallback, and return correct result
    res, used_backend, error = scheduler.execute_with_fallback(
        primary_fn=failing_fn,
        fallback_fn=fallback_fn,
        args=(x,),
        primary_backend="OPENCL_IGPU",
        fallback_backend="CPU_AVX2",
    )

    assert used_backend == "CPU_AVX2"
    assert error is not None
    assert "Simulated OpenCL launch crash" in error
    assert np.allclose(res, x * 2.0)
