"""
tests/test_usm_scheduler.py
===========================
Unit tests for the Zero-Copy Heterogeneous USM Scheduler.
Verifies unified shared memory allocation, hardware core pinning,
and in-place iGPU boolean mask evaluation.
"""

import numpy as np
import pytest

from hyper.research_engine.usm_scheduler import USMManager
from hyper.research_engine.resource_compiler import HeterogeneousResourceCompiler, ExecutionDevice


def test_usm_allocate_and_free():
    shape = (128, 128)
    arr = USMManager.allocate_shared(shape, dtype=np.float32)
    assert arr.shape == shape
    assert arr.dtype == np.float32
    # Modify data
    arr[0, 0] = 42.0
    assert arr[0, 0] == 42.0
    USMManager.free_shared(arr)


def test_usm_pinning_pcores_and_ecores():
    # Pinning should execute safely without runtime exceptions
    p_ok = USMManager.pin_to_pcores()
    assert isinstance(p_ok, bool)
    e_ok = USMManager.pin_to_ecores()
    assert isinstance(e_ok, bool)


def test_usm_zero_copy_masking():
    # Create target buffer and mask buffer
    target = np.array([0xFFFFFFFF, 0x12345678, 0xAAAAAAAA], dtype=np.uint32)
    mask   = np.array([0x0000FFFF, 0x00000000, 0x55555555], dtype=np.uint32)

    USMManager.apply_igpu_mask(target, mask)

    expected = np.array([0x0000FFFF, 0x00000000, 0x00000000], dtype=np.uint32)
    assert np.array_equal(target, expected)


def test_usm_heterogeneous_resource_compiler_routing():
    # Large multi-stage payload should be routed to HETEROGENEOUS_PIPELINE
    plan = HeterogeneousResourceCompiler.compile_resource_plan(
        total_flops=1e9,
        input_bytes=4 * 1024 * 1024,
        output_bytes=4 * 1024 * 1024,
        is_fused_pipeline=True,
    )
    assert plan.selected_device in (
        ExecutionDevice.HETEROGENEOUS_PIPELINE,
        ExecutionDevice.INTEL_IGPU,
    )
    assert plan.dram_traffic_eliminated_pct > 0.0


def test_usm_pipeline_overlap_measurement():
    def compute_a():
        s = 0
        for i in range(10000):
            s += i
        return s

    def compute_b():
        s = 1
        for i in range(1, 10000):
            s ^= i
        return s

    res_a, res_b, overlap_ms = HeterogeneousResourceCompiler.execute_with_measured_overlap(
        compute_a, compute_b
    )
    assert res_a == sum(range(10000))
    assert isinstance(overlap_ms, float)
    assert overlap_ms >= 0.0


def test_opencl_zero_copy_hardware_execution():
    from hyper.extreme.opencl_uva import OpenCLZeroCopyUVA
    uva = OpenCLZeroCopyUVA()
    if uva.is_available:
        assert "Intel" in uva.device_name
        assert uva.compute_units == 48
        assert uva.host_unified_memory is True

        # Test zero-copy hardware mask
        target = np.array([0xFF00FF00, 0xAAAAAAAA], dtype=np.uint32)
        mask = np.array([0x0F0F0F0F, 0x55555555], dtype=np.uint32)
        res, meta = uva.execute_zero_copy_boolean_mask(target, mask)
        assert meta["is_zero_copy"] is True
        assert meta["copy_overhead_bytes"] == 0
        assert res[0] == (0xFF00FF00 & 0x0F0F0F0F)
        assert res[1] == (0xAAAAAAAA & 0x55555555)

        # Test zero-copy hardware VSA popcount
        a = np.array([0xFFFFFFFF, 0x00000000], dtype=np.uint32)
        b = np.array([0x00000000, 0xFFFFFFFF], dtype=np.uint32)
        counts, meta2 = uva.execute_zero_copy_vsa_popcount(a, b)
        assert meta2["is_zero_copy"] is True
        assert counts[0] == 32
        assert counts[1] == 32
