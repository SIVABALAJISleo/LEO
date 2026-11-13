"""
tests/test_intel_alderlake_unlocker.py
======================================
Comprehensive test suite for Intel Alder Lake i5-12450H & Intel UHD iGPU:
  1. Windows 11 EcoQoS throttle bypass, process priority elevation, 1.0 ms timer resolution.
  2. 4096-byte page-aligned Zero-Copy USM host buffer allocation.
  3. AVX-VNNI INT8 GEMV hardware execution with exact integer parity & cosine similarity.
  4. FunctionalReplacementEngine integration and benchmark verification.
"""

import sys
import numpy as np
import pytest

from backend.canonical.intel_alderlake_unlocker import (
    unlock_windows11_alderlake_throttles,
    allocate_zero_copy_page_aligned_buffer,
    execute_avx_vnni_gemv,
    benchmark_intel_alderlake_acceleration,
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


def test_unlock_windows11_alderlake_throttles():
    """Validates that unlock_windows11_alderlake_throttles executes safely without unhandled errors."""
    status = unlock_windows11_alderlake_throttles()
    assert isinstance(status, dict)
    assert "platform" in status
    assert "ecoqos_throttle_disabled" in status
    assert "high_priority_enabled" in status
    assert "timer_1ms_unlocked" in status

    if sys.platform == "win32":
        assert status["platform"] == "win32"
        # On Windows 11, timer unlocking should succeed
        assert status["timer_1ms_unlocked"] is True
        assert status["ecoqos_throttle_disabled"] is True
        assert status["high_priority_enabled"] is True


def test_allocate_zero_copy_page_aligned_buffer():
    """Validates 4096-byte page alignment and 64-byte cacheline alignment across multiple shapes/dtypes."""
    test_cases = [
        ((1024,), np.float32),
        ((256, 256), np.float32),
        ((128, 64, 32), np.int8),
        ((512, 512), np.uint8),
        ((64, 128), np.int32),
        ((100, 200), np.float64),
    ]

    for shape, dt in test_cases:
        buf, meta = allocate_zero_copy_page_aligned_buffer(shape, dtype=dt)
        addr = int(buf.ctypes.data)

        # Strict hardware alignment contracts
        assert meta["page_aligned_4096"] is True, f"Failed 4096-byte page alignment for shape {shape}"
        assert meta["cacheline_aligned_64"] is True, f"Failed 64-byte cacheline alignment for shape {shape}"
        assert addr % 4096 == 0, f"Virtual address {hex(addr)} not divisible by 4096"
        assert addr % 64 == 0, f"Virtual address {hex(addr)} not divisible by 64"
        assert buf.shape == shape
        assert buf.dtype == np.dtype(dt)

        # Verify data writeability
        buf.fill(42)
        assert np.all(buf == 42)


def test_execute_avx_vnni_gemv_exact_numerical():
    """Validates AVX-VNNI INT8 GEMV against exact algebraic reference across multiple K multiples."""
    rng = np.random.default_rng(42)

    configs = [
        (1, 32),
        (8, 64),
        (32, 128),
        (64, 256),
        (128, 512),
        (16, 35),   # Non-multiple of 32 to test scalar tail
        (32, 67),   # Non-multiple of 32 to test scalar tail
    ]

    for m_dim, k_dim in configs:
        a_u8 = rng.integers(0, 256, size=k_dim, dtype=np.uint8)
        b_s8 = rng.integers(-128, 127, size=(m_dim, k_dim), dtype=np.int8)

        c_actual = execute_avx_vnni_gemv(a_u8, b_s8)
        c_expected = (b_s8.astype(np.int32) @ a_u8.astype(np.int32)).astype(np.int32)

        # Exact integer match
        np.testing.assert_array_equal(c_actual, c_expected)

        # Cosine similarity contract
        c_norm = float(np.linalg.norm(c_actual))
        exp_norm = float(np.linalg.norm(c_expected))
        if c_norm > 0 and exp_norm > 0:
            cos_similarity = float(np.dot(c_actual.astype(np.float64), c_expected.astype(np.float64)) / (c_norm * exp_norm))
            assert cos_similarity >= 0.999


def test_execute_avx_vnni_gemv_error_handling():
    """Validates proper error raises on mismatched dimensions or invalid shapes."""
    a_u8 = np.ones(32, dtype=np.uint8)
    b_s8_mismatch = np.ones((8, 64), dtype=np.int8)

    with pytest.raises(ValueError, match="Dimension mismatch"):
        execute_avx_vnni_gemv(a_u8, b_s8_mismatch)

    b_s8_3d = np.ones((2, 4, 32), dtype=np.int8)
    with pytest.raises(ValueError, match="must be a 2D matrix"):
        execute_avx_vnni_gemv(a_u8, b_s8_3d)


def test_functional_replacement_engine_integration():
    """Validates FunctionalReplacementEngine dispatch methods for Alder Lake unlocker."""
    engine = FunctionalReplacementEngine()

    unlock_res = engine.unlock_intel_alderlake_throttles()
    assert isinstance(unlock_res, dict)

    buf, meta = engine.allocate_usm_buffer((128, 128), dtype=np.float32)
    assert meta["page_aligned_4096"] is True
    assert meta["cacheline_aligned_64"] is True

    a_u8 = np.arange(32, dtype=np.uint8)
    b_s8 = np.ones((4, 32), dtype=np.int8)
    c_out = engine.execute_avx_vnni_int8_gemv(a_u8, b_s8)
    assert c_out.shape == (4,)
    np.testing.assert_array_equal(c_out, (b_s8.astype(np.int32) @ a_u8.astype(np.int32)))

    bench_res = engine.benchmark_alderlake_acceleration()
    assert bench_res["passed"] is True
    assert bench_res["page_aligned_4096"] is True
    assert bench_res["exact_integer_match"] is True


def test_benchmark_intel_alderlake_acceleration():
    """Validates the complete hardware acceleration benchmark runner."""
    report = benchmark_intel_alderlake_acceleration()
    assert report["passed"] is True
    assert report["page_aligned_4096"] is True
    assert report["cacheline_aligned_64"] is True
    assert report["exact_integer_match"] is True
    assert report["cosine_similarity"] >= 0.999
    assert report["throughput_gops"] > 0.0
    assert report["latency_ms"] > 0.0

