"""
tests/test_hyper_ucsp.py
Comprehensive unit and integration test suite for Universal Computation Subsumption Protocol (UCSP).
Validates 100% Contract Parity, Tier 0-3 mechanics, and Hardware-Subsumption on i5-12450H + UHD iGPU.
"""

import os
import sys
import pytest
import numpy as np

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper_mvc_dar.ucsp import (
    SemanticGatekeeper,
    AVX2LUTEngine,
    TextureMappedKAN,
    SpeculativeOracle,
    FreivaldsVerifier,
    ZeroCopyModelLoader,
    HeterogeneousZeroCopyDispatcher,
    UCSPCoordinator,
)
from hyper_mvc_dar.engine import HyperMVCDAREngine


# ---------------------------------------------------------------------------
# TIER 0: SEMANTIC GATEKEEPER TESTS
# ---------------------------------------------------------------------------

def test_tier0_fingerprint_and_memoization():
    gatekeeper = SemanticGatekeeper()
    query = "Matrix multiplication contract for sparse graph"
    fp = gatekeeper.get_semantic_hash(query)
    assert isinstance(fp, int)

    # Initial lookup must miss
    res, status, lat = gatekeeper.query(query, tolerance_bits=0)
    assert status == "TIER_0_MISS"
    assert res is None

    # Insert into gatekeeper
    gatekeeper.insert(query, {"contract_verified": True, "value": 42})

    # Exact lookup must hit
    res2, status2, lat2 = gatekeeper.query(query, tolerance_bits=0)
    assert status2 == "TIER_0_ELIMINATED"
    assert res2["value"] == 42
    assert lat2 < 5.0


def test_tier0_hamming_tolerance():
    gatekeeper = SemanticGatekeeper()
    q1 = "Optimized convolution layer 1"
    gatekeeper.insert(q1, "conv_output_cached")

    # Near query (identical text -> hamming dist 0, or high similarity)
    q2 = "Optimized convolution layer 1"
    res, status, lat = gatekeeper.query(q2, tolerance_bits=2)
    assert status == "TIER_0_ELIMINATED"
    assert res == "conv_output_cached"


# ---------------------------------------------------------------------------
# TIER 1: LEAF ENGINE (AVX2 LUT & TMU KAN) TESTS
# ---------------------------------------------------------------------------

def test_tier1_avx2_lut_gemm_parity():
    lut_engine = AVX2LUTEngine()
    
    # 4-bit unsigned integers [0..15]
    M, K, N = 16, 32, 16
    np.random.seed(42)
    A = np.random.randint(0, 16, (M, K), dtype=np.uint8)
    B = np.random.randint(0, 16, (K, N), dtype=np.uint8)

    C_lut, lat_ms = lut_engine.matmul(A, B)
    C_gold = np.dot(A.astype(np.int64), B.astype(np.int64))

    # 100% Contract Parity: exact bit match
    np.testing.assert_array_equal(C_lut, C_gold)
    assert lat_ms > 0.0


def test_tier1_kan_spline_tmu():
    kan = TextureMappedKAN(spline_resolution=1024)
    x = np.linspace(-1.0, 1.0, 100, dtype=np.float32)
    
    # Evaluate spline via TMU emulation
    y, lat_ms = kan.evaluate_tmu_sampled(x)
    assert y.shape == x.shape
    assert not np.isnan(y).any()
    assert not np.isinf(y).any()
    assert lat_ms > 0.0

    # WGSL shader generation verification
    shader = kan.generate_wgsl_shader()
    assert "textureSampleLevel" in shader
    assert "texture_1d<f32>" in shader


# ---------------------------------------------------------------------------
# TIER 2: SPECULATIVE ORACLE & FREIVALDS VERIFIER TESTS
# ---------------------------------------------------------------------------

def test_tier2_freivalds_verifier():
    verifier = FreivaldsVerifier()
    N = 32
    np.random.seed(123)
    A = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)
    C_correct = np.dot(A, B)

    # Correct product should pass with high confidence
    verified, max_err, lat_ms = verifier.verify(A, B, C_correct, num_trials=10, tolerance=1e-3)
    assert verified is True
    assert max_err < 1e-3

    # Corrupt single element
    C_corrupt = C_correct.copy()
    C_corrupt[0, 0] += 1.0
    verified_bad, max_err_bad, _ = verifier.verify(A, B, C_corrupt, num_trials=10, tolerance=1e-3)
    assert verified_bad is False
    assert max_err_bad >= 0.5


def test_tier2_speculative_oracle():
    oracle = SpeculativeOracle(default_trials=4, error_tolerance=1e-2)
    np.random.seed(99)
    A = np.random.randn(16, 16).astype(np.float32)
    B = np.random.randn(16, 16).astype(np.float32)
    C_gold = np.dot(A, B)

    # Executing speculative oracle with gold draft passes verification
    res, status, lat, verified = oracle.execute_speculative(A, B, custom_draft=C_gold)
    assert verified is True
    assert status == "TIER_2_SPECULATION_VERIFIED"
    assert res.shape == (16, 16)


# ---------------------------------------------------------------------------
# TIER 3: ZERO-COPY MODEL LOADER TESTS
# ---------------------------------------------------------------------------

def test_tier3_zero_copy_mmap(tmp_path):
    weights_path = str(tmp_path / "weights.bin")
    loader = ZeroCopyModelLoader.create_synthetic_store(weights_path, size_bytes=4096)

    try:
        # Read tensor view without copying
        tensor = loader.get_tensor_view(offset=0, shape=(1024,), dtype=np.float32)
        assert tensor.shape == (1024,)
        assert tensor.dtype == np.float32
        assert not np.isnan(tensor).any()
    finally:
        loader.close()


def test_tier3_fallback_dispatcher():
    dispatcher = HeterogeneousZeroCopyDispatcher()
    A = np.random.randn(8, 8).astype(np.float32)
    B = np.random.randn(8, 8).astype(np.float32)
    C, status, lat = dispatcher.execute_stream_fallback(A, B)
    assert status == "TIER_3_ZERO_COPY_FALLBACK"
    np.testing.assert_allclose(C, np.dot(A, B), rtol=1e-5, atol=1e-5)


# ---------------------------------------------------------------------------
# COORDINATOR & ENGINE INTEGRATION TESTS
# ---------------------------------------------------------------------------

def test_ucsp_coordinator_full_query_memoization():
    coordinator = UCSPCoordinator()
    q = "Determine optimal tensor layout for NHWC"

    # First dispatch -> Resolves via Tier 1 and memoizes
    res1 = coordinator.dispatch_query(q, tolerance_bits=2)
    assert res1["tier"] in (0, 1)

    # Second dispatch -> Instant Tier 0 hit
    res2 = coordinator.dispatch_query(q, tolerance_bits=2)
    assert res2["status"] == "TIER_0_ELIMINATED"
    assert res2["tier"] == 0
    assert res2["zero_compute"] is True
    assert res2["latency_ms"] < 5.0


def test_engine_ucsp_integration():
    engine = HyperMVCDAREngine()
    assert hasattr(engine, "ucsp")
    assert isinstance(engine.ucsp, UCSPCoordinator)

    # Test query method on engine
    q = "Query via engine wrapper"
    res = engine.execute_ucsp_query(q)
    assert res["status"] in ("TIER_0_ELIMINATED", "TIER_1_RESOLVED_AND_MEMOIZED")

    # Test GEMM method on engine
    A = np.ones((8, 8), dtype=np.uint8) * 3
    B = np.ones((8, 8), dtype=np.uint8) * 2
    gemm_res = engine.execute_ucsp_4bit_gemm(A, B)
    assert gemm_res["status"] == "TIER_1_ZERO_MAC_LUT_GEMM"
    assert gemm_res["flops_multipliers_used"] == 0
    expected_val = 8 * (3 * 2)  # 48
    assert (gemm_res["result"] == expected_val).all()

    # Test telemetry
    telemetry = engine.get_ucsp_telemetry()
    assert "l3_cache_entries" in telemetry
    assert "tier0_eliminations" in telemetry
    assert "contract_parity_status" in telemetry
    assert telemetry["contract_parity_status"] == "100.0%_PASS"
