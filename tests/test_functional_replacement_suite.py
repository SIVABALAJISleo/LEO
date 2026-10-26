"""
tests/test_functional_replacement_suite.py
===========================================
Verification and Falsification Suite for Project LEO's Functional Replacement Engine.

Tests:
  1. Subsystem A: CUR Skeleton Factoring on clean low-rank matrices.
  2. Subsystem A: CUR Adversarial Spike Rejection via Output-Side Batched Freivalds.
  3. Subsystem A: CUR Pre-Filter Fast Rejection on full-rank white noise.
  4. Subsystem B: Offline Truncated SVD on decaying singular spectra.
  5. Subsystem B: Offline SVD Dense Retention when low-rank is unfavorable.
  6. Subsystem C: Live 2-Bit Ternary Packing with MMSE scales and live compression accounting.
  7. Subsystem C: Live INT4 2x Packing with live ratio computation.
  8. Subsystem C: Out-of-Core NVMe Block Tiling with memmap backing and streaming throughput.
  9. Subsystem D: Native Runtime Bridge for llama.cpp and Intel UHD 48-EU iGPU execution.
 10. Strict Ledger Anti-Mock Verification: Zero mock fallbacks allowed.
"""

import os
import numpy as np
import pytest

from backend.canonical.functional_replacement_engine import (
    FunctionalReplacementEngine,
    CurSkeletonFactoringResult,
    OfflineTruncatedSVDResult,
    QuantizedBitPackingResult,
    OutOfCoreTileResult,
)
from backend.canonical.native_runtime_bridge import NativeRuntimeBridge
from backend.core.errors import MockFallbackForbiddenError
from hyper_runtime.hyper_fabric_orchestrator import DragonLogicEngine


@pytest.fixture
def engine():
    return FunctionalReplacementEngine(seed=42)


@pytest.fixture
def bridge():
    return NativeRuntimeBridge()


# ── Subsystem A: CUR Skeleton Factoring & Batched Freivalds ──────────────────

def test_subsystem_a_cur_skeleton_factoring_clean_low_rank(engine):
    """Verify that a clean low-rank matrix passes both pre-filter and Freivalds verification."""
    # A = U @ V where rank is 6, dimensions 256 x 256
    rng = np.random.default_rng(101)
    U = rng.standard_normal((256, 6)).astype(np.float32)
    V = rng.standard_normal((6, 256)).astype(np.float32)
    A = U @ V
    B = rng.standard_normal((256, 128)).astype(np.float32)

    res = engine.cur_skeleton_gemm(A, B, c_samples=32, epsilon_tol=1e-3)

    assert res.prefilter_passed is True
    assert res.freivalds_passed is True
    assert res.executed_mode == "CUR_ACCELERATED"
    assert res.is_mock is False

    # Check exact mathematical error vs ground truth A @ B
    exact = A @ B
    rel_err = np.linalg.norm(res.result - exact) / (np.linalg.norm(exact) + 1e-12)
    assert rel_err < 1e-3


def test_subsystem_a_cur_adversarial_spike_rejection(engine):
    """
    Verify that an adversarial spike hidden outside the sampled rows and columns
    is caught by the mandatory output-side batched Freivalds probe, triggering
    an automatic fallback to exact A @ B.
    """
    rng = np.random.default_rng(102)
    U = rng.standard_normal((256, 4)).astype(np.float32)
    V = rng.standard_normal((4, 256)).astype(np.float32)
    A = U @ V
    B = rng.standard_normal((256, 128)).astype(np.float32)

    # Inject an adversarial spike in an interior position NOT on the strided sample grid
    # Strided grid uses steps; we pick an odd off-grid index
    spike_i, spike_j = 127, 127
    A[spike_i, spike_j] += 1000.0

    res = engine.cur_skeleton_gemm(A, B, c_samples=16, epsilon_tol=1e-3)

    # Either pre-filter or Freivalds must catch this violation!
    assert res.executed_mode in (
        "EXACT_FALLBACK_FREIVALDS_REJECTED",
        "EXACT_FALLBACK_PREFILTER_REJECTED",
    )
    # The output must be the exact product A @ B despite the shortcut failure
    exact = A @ B
    np.testing.assert_allclose(res.result, exact, rtol=1e-4, atol=1e-4)


def test_subsystem_a_cur_prefilter_fast_rejection_on_white_noise(engine):
    """Full-rank Gaussian white noise cannot be low-rank factored and must be rejected quickly."""
    rng = np.random.default_rng(103)
    A = rng.standard_normal((128, 128)).astype(np.float32)
    B = rng.standard_normal((128, 64)).astype(np.float32)

    res = engine.cur_skeleton_gemm(A, B, c_samples=16, epsilon_tol=1e-4)

    assert res.prefilter_passed is False
    assert res.executed_mode == "EXACT_FALLBACK_PREFILTER_REJECTED"
    assert res.rejection_flag is not None
    # Result must still be exact
    exact = A @ B
    np.testing.assert_allclose(res.result, exact, rtol=1e-5, atol=1e-5)


# ── Subsystem B: Offline Truncated SVD ───────────────────────────────────────

def test_subsystem_b_offline_truncated_svd_decaying_spectrum(engine):
    """Verify offline truncated SVD factors weight matrices with rapidly decaying spectra."""
    rng = np.random.default_rng(104)
    M, N = 256, 256
    # Construct synthetic weight matrix with polynomial spectral decay sigma_i = i^(-1.5)
    U, _ = np.linalg.qr(rng.standard_normal((M, M)))
    V, _ = np.linalg.qr(rng.standard_normal((N, N)))
    singular_values = np.array([float(i) ** (-1.5) for i in range(1, M + 1)], dtype=np.float32)
    W = (U * singular_values[np.newaxis, :]) @ V.T

    # Prepare model offline
    prepared = engine.prepare_offline_truncated_svd(W, epsilon_contract=1e-2)

    assert prepared["is_dense_retained"] is False
    assert prepared["rank_r"] < (M * N) // (M + N)  # Below breakeven
    assert prepared["setup_load_ms"] > 0.0

    # Online inference pass
    X = rng.standard_normal((8, M)).astype(np.float32)
    infer_res = engine.execute_truncated_svd_inference(X, prepared)

    assert infer_res.output.shape == (8, N)
    exact_out = X @ W
    rel_err = np.linalg.norm(infer_res.output - exact_out) / np.linalg.norm(exact_out)
    assert rel_err < 0.02


def test_subsystem_b_offline_truncated_svd_dense_retention(engine):
    """Verify that full-rank matrices without decaying spectra retain dense representation."""
    rng = np.random.default_rng(105)
    # High-entropy random matrix (equal singular values)
    W = rng.standard_normal((64, 64)).astype(np.float32)

    prepared = engine.prepare_offline_truncated_svd(W, epsilon_contract=1e-4)

    assert prepared["is_dense_retained"] is True
    assert prepared["u_sigma"] is None
    assert prepared["vt"] is None


# ── Subsystem C: Live Bit-Packed Quantization & NVMe Out-of-Core ─────────────

def test_subsystem_c_ternary_2bit_packing_and_live_ratio(engine):
    """Verify bitwise packing of 4 ternary values into 1 uint8 byte with live ratio accounting."""
    rng = np.random.default_rng(106)
    W = rng.standard_normal((64, 64)).astype(np.float32)

    pack_res = engine.pack_ternary_2bit(W)

    assert pack_res.mode == "TERNARY_2BIT"
    assert pack_res.packed_nbytes == (64 * 64) // 4  # 4 ternary values per byte
    # Ratio must be computed live from nbytes
    assert pack_res.measured_compression_ratio > 3.0
    assert pack_res.reconstructed.shape == (64, 64)
    assert pack_res.is_mock is False


def test_subsystem_c_int4_2x_packing_and_reconstruction(engine):
    """Verify bitwise packing of 2 INT4 values into 1 uint8 byte."""
    rng = np.random.default_rng(107)
    W = rng.standard_normal((64, 64)).astype(np.float32)

    pack_res = engine.pack_int4_2x(W)

    assert pack_res.mode == "INT4_2X_PACKED"
    assert pack_res.packed_nbytes == (64 * 64) // 2  # 2 INT4 values per byte
    assert pack_res.measured_compression_ratio > 1.8
    assert pack_res.reconstructed.shape == (64, 64)
    assert pack_res.is_mock is False


def test_subsystem_c_out_of_core_tiling_memmap(engine):
    """Verify tiled block multiplication backed by np.memmap on NVMe SSD."""
    res = engine.execute_out_of_core_tiling(
        M=512, K=512, N=512, tile_size=256, force_out_of_core=True
    )

    assert res.backed_by_nvme_memmap is True
    assert res.tiles_m == 2
    assert res.tiles_n == 2
    assert res.tiles_k == 2
    assert res.sample_corner_verified is True
    assert res.streaming_throughput_mb_s > 0.0
    assert res.effective_gflops > 0.0
    assert res.is_mock is False


# ── Subsystem D: Native Runtime Bridge ───────────────────────────────────────

def test_subsystem_d_native_runtime_bridge(bridge):
    """Verify NativeRuntimeBridge safely probes binaries and runs iGPU offload."""
    # Test llama.cpp probe (honest handling when GGUF model is not provided)
    bench_res = bridge.benchmark_llama_cpp("nonexistent_model.gguf")
    assert bench_res.is_mock is False

    # Test iGPU / CPU offload execution
    x = np.ones((4, 32), dtype=np.float32)
    w = np.eye(32, dtype=np.float32) * 2.0
    offload_res = bridge.offload_to_intel_igpu("BATCH_PREFILL", input_tensor=x, aux_tensor=w)

    assert offload_res.execution_latency_ms >= 0.0
    assert offload_res.output_shape == (4, 32)
    assert offload_res.output_norm > 0.0
    assert offload_res.is_mock is False


# ── Strict Ledger Anti-Mock Verification ─────────────────────────────────────

def test_strict_ledger_dragon_engine_no_mocks():
    """Verify that DragonLogicEngine under strict ledger produces verified results with is_mock=False."""
    engine = DragonLogicEngine()
    res = engine.handle_request("analyze quantum matrix transformations")

    assert res["is_mock"] is False
    assert res["latency_ms"] >= 0.0
    assert res["engine_used"] in (
        "sparse_expert_native",
        "bitnet_cpu_native",
        "semantic_replay",
        "symbolic_logic",
        "speculative_decoding",
    )
