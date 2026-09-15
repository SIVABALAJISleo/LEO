"""
tests/test_extreme_heterogeneous.py
===================================
Automated verification suite for Extreme Software-Only Heterogeneous Parity &
Breakthrough Optimization on Intel Core i5-12450H + Intel UHD Graphics.
"""

import numpy as np
import pytest

from hyper.extreme.tbiqs import (
    TBIQSEngine,
    QuantizedTensor,
    L3_WORKING_SET_CEILING_BYTES,
)
from hyper.extreme.opencl_uva import OpenCLZeroCopyUVA
from hyper.extreme.lut_arithmetic import LUTArithmeticEngine, MorphingLUT
from hyper.extreme.cdre import CDREFramework, CDRETelemetry
from hyper.extreme.affinity_scheduler import AlderLakeAffinityScheduler


class TestTBIQSEngine:
    """Tests for Tile-Based In-Cache Quantized Streaming Engine."""

    def test_quantization_and_compression_ratios(self):
        engine_4bit = TBIQSEngine(default_bits=4, default_block_size=32)
        engine_2bit = TBIQSEngine(default_bits=2, default_block_size=32)

        tensor = np.random.uniform(-2.0, 2.0, (128, 128)).astype(np.float32)

        # 4-bit test
        q4 = engine_4bit.quantize(tensor)
        assert q4.bits == 4
        assert q4.element_count == 128 * 128
        assert q4.is_l3_resident is True
        assert q4.compression_ratio_vs_fp32 >= 4.0

        # Dequantize and check numerical range
        recon_4 = engine_4bit.dequantize(q4)
        assert recon_4.shape == tensor.shape
        rel_err_4 = np.linalg.norm(recon_4 - tensor) / np.linalg.norm(tensor)
        assert rel_err_4 < 0.15  # 4-bit quantization error bound

        # 2-bit test
        q2 = engine_2bit.quantize(tensor)
        assert q2.bits == 2
        assert q2.compression_ratio_vs_fp32 >= 7.0
        assert q2.is_l3_resident is True

    def test_l3_working_set_ceiling(self):
        engine = TBIQSEngine(default_bits=4)
        # 1024x1024 matrix in FP32 is 4 MB; two matrices + accumulator would be 12 MB
        # In 4-bit, 1024x1024 is ~0.6 MB, well below 9.6 MB
        A = np.random.randn(512, 512).astype(np.float32)
        qA = engine.quantize(A)
        assert qA.packed_bytes < L3_WORKING_SET_CEILING_BYTES
        assert qA.is_l3_resident is True

    def test_tiled_gemm_in_cache(self):
        engine = TBIQSEngine(default_bits=4, default_block_size=32)
        A = np.random.uniform(0.1, 1.0, (64, 64)).astype(np.float32)
        B = np.random.uniform(0.1, 1.0, (64, 64)).astype(np.float32)

        qA = engine.quantize(A)
        qB = engine.quantize(B)

        C_tiled = engine.tiled_gemm_in_cache(qA, qB)
        C_ref = np.matmul(A, B)

        assert C_tiled.shape == (64, 64)
        rel_diff = np.linalg.norm(C_tiled - C_ref) / np.linalg.norm(C_ref)
        assert rel_diff < 0.15


class TestOpenCLZeroCopyUVA:
    """Tests for Zero-Copy Unified Virtual Addressing on Intel UHD Graphics."""

    def test_uva_device_discovery(self):
        uva = OpenCLZeroCopyUVA()
        if uva.is_available:
            assert "Intel" in uva.device_name or "UHD" in uva.device_name or uva.compute_units > 0
            assert uva.host_unified_memory is True

    def test_zero_copy_gemm_execution(self):
        uva = OpenCLZeroCopyUVA()
        A = np.random.uniform(-1.0, 1.0, (64, 64)).astype(np.float32)
        B = np.random.uniform(-1.0, 1.0, (64, 64)).astype(np.float32)
        C_ref = np.matmul(A, B)

        C_uva, meta = uva.execute_zero_copy_gemm(A, B)
        assert C_uva.shape == (64, 64)

        max_err = float(np.max(np.abs(C_uva - C_ref)))
        assert max_err < 1e-4, f"Error {max_err} exceeds contract tolerance"

        if meta.get("backend") == "INTEL_UHD_OPENCL_ZERO_COPY":
            assert meta["is_zero_copy"] is True
            assert meta["copy_overhead_bytes"] == 0


class TestLUTArithmeticEngine:
    """Tests for Bit-Level Arithmetic Morphing with LUT Lookups."""

    def test_lut_construction_and_local_memory_budget(self):
        engine4 = LUTArithmeticEngine(bits=4)
        assert engine4.lut.table.shape == (16, 16)
        assert engine4.lut.table_bytes == 16 * 16 * 4  # 1024 bytes
        assert engine4.lut.fits_in_local_memory is True

        engine2 = LUTArithmeticEngine(bits=2)
        assert engine2.lut.table.shape == (4, 4)
        assert engine2.lut.table_bytes == 4 * 4 * 4   # 64 bytes
        assert engine2.lut.fits_in_local_memory is True

    def test_cpu_lut_matmul(self):
        engine = LUTArithmeticEngine(bits=4)
        tbiqs = TBIQSEngine(default_bits=4)

        A = np.random.uniform(0.1, 1.0, (32, 32)).astype(np.float32)
        B = np.random.uniform(0.1, 1.0, (32, 32)).astype(np.float32)
        qA = tbiqs.quantize(A)
        qB = tbiqs.quantize(B)

        C_lut, meta = engine.cpu_lut_matmul(qA, qB)
        assert C_lut.shape == (32, 32)
        assert meta["floating_point_multiplies_eliminated"] == 32 * 32 * 32
        assert meta["lut_size_bytes"] == 1024


class TestCDREFramework:
    """Tests for Contract-Driven Redundancy Elimination Framework."""

    def test_structural_hash_invariance(self):
        cdre = CDREFramework()
        t1 = np.ones((64, 64), dtype=np.float32)
        t2 = np.ones((64, 64), dtype=np.float32)

        h1 = cdre.compute_structural_hash(t1, extra_tag="op1")
        h2 = cdre.compute_structural_hash(t2, extra_tag="op1")
        assert h1 == h2

        t3 = np.zeros((64, 64), dtype=np.float32)
        h3 = cdre.compute_structural_hash(t3, extra_tag="op1")
        assert h1 != h3

    def test_dead_dependency_pruning(self):
        cdre = CDREFramework()
        graph = [
            {"name": "load_weights", "inputs": [], "out": "W"},
            {"name": "dead_bias_transform", "inputs": ["W"], "out": "dead_bias"},
            {"name": "matmul", "inputs": ["X", "W"], "out": "Y"},
        ]
        active, pruned = cdre.prune_dead_dependencies(graph, output_keys={"Y"})
        assert pruned == 1
        active_names = [n["name"] for n in active]
        assert "dead_bias_transform" not in active_names
        assert "matmul" in active_names
        assert "load_weights" in active_names

    def test_contract_execution_caching(self):
        cdre = CDREFramework(tolerance=1e-4)
        A = np.random.randn(16, 16).astype(np.float32)
        B = np.random.randn(16, 16).astype(np.float32)

        call_count = [0]
        def fast_gemm():
            call_count[0] += 1
            return np.matmul(A, B)

        # Pass 1: Miss
        res1, telem1 = cdre.execute_under_contract("test_op", fast_gemm, lambda: np.matmul(A, B), [A, B])
        assert telem1.cache_hit is False
        assert call_count[0] == 1

        # Pass 2: Invariant Cache Hit
        res2, telem2 = cdre.execute_under_contract("test_op", fast_gemm, lambda: np.matmul(A, B), [A, B])
        assert telem2.cache_hit is True
        assert telem2.work_eliminated_ratio == 1.0
        assert call_count[0] == 1  # Fast function was NOT called again!
        np.testing.assert_allclose(res1, res2)

    def test_drift_detection_fail_closed_fallback(self):
        cdre = CDREFramework(tolerance=1e-4)
        A = np.random.randn(16, 16).astype(np.float32)
        B = np.random.randn(16, 16).astype(np.float32)

        # Candidate has huge drift (error > 10^-4)
        def bad_fast_gemm():
            return np.matmul(A, B) + 10.0

        res, telem = cdre.execute_under_contract(
            "drift_op",
            bad_fast_gemm,
            lambda: np.matmul(A, B),
            [A, B],
            allow_cache=False,
        )
        assert telem.drift_detected is True
        assert telem.fallback_triggered is True
        # Exact fallback was returned
        np.testing.assert_allclose(res, np.matmul(A, B))


class TestAlderLakeAffinityScheduler:
    """Tests for Alder Lake Core Affinity Pinning Scheduler."""

    def test_topology_detection(self):
        sched = AlderLakeAffinityScheduler()
        assert sched.topology.total_logical >= 8
        assert len(sched.p_cores) > 0
        assert len(sched.e_cores) > 0
        # Check P-core and E-core indices do not overlap
        assert set(sched.p_cores).isdisjoint(set(sched.e_cores))

    def test_pin_p_cores_context(self):
        sched = AlderLakeAffinityScheduler()
        initial_aff = sched.get_current_affinity()

        with sched.pin_p_cores():
            current_aff = sched.get_current_affinity()
            assert current_aff == sched.p_cores

        # Restores initial
        assert sched.get_current_affinity() == initial_aff
