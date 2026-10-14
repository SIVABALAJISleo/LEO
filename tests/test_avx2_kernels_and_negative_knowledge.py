"""
tests/test_avx2_kernels_and_negative_knowledge.py
===================================================
Automated validation of:
1. Section 14 Scientific Negative Knowledge:
   - Direct SVD Factorization on Full-Rank Gaussian Noise rejection (energy ratio >= 0.95 rule).
   - Small-Scale OpenCL Offloading (< 256 KB) dispatch thresholding.
   - Double-Buffering Prefetch thresholding (< 8 MB synchronous, >= 8 MB async double-buffered).
2. Section 16 AVX2 High-Performance Compiled Extension Modules:
   - 2:4 Structured Sparsity Engine (pruning, packing, and AVX2 compiled GEMM).
   - BitNet 1.58b Ternary Dot Product Engine (pure addition/subtraction GEMM, 16x compression).
"""

import os
import tempfile
import pytest
import numpy as np

from hyper_universal.transformation_dsl.library import LowRankSVDTransformation
from hyper_universal.scheduler.scheduler import UniversalScheduler
from hyper_universal.memory_escape.engine import OutOfCoreStreamEngine
from hyper_universal.kernels.sparse_2_4_avx2 import (
    prune_and_pack_2_4,
    gemm_2_4_sparse_avx2,
    StructuredSparse24Engine,
)
from hyper_universal.kernels.bitnet_ternary_avx2 import (
    quantize_to_bitnet_ternary,
    bitnet_ternary_gemm_avx2,
    BitNetTernaryEngine,
)


def test_svd_full_rank_gaussian_noise_rejected():
    """Verify that full-rank Gaussian noise is rejected due to energy ratio < 0.95."""
    np.random.seed(42)
    # Full-rank Gaussian white noise matrix has a flat singular spectrum
    A_noise = np.random.randn(128, 128).astype(np.float32)

    svd_xf = LowRankSVDTransformation(target_rank=16, min_energy_ratio=0.95)
    valid, msg = svd_xf.check_preconditions(A_noise)

    assert not valid
    assert "Singular value energy ratio" in msg
    assert "full-rank Gaussian noise detected" in msg

    # Applying must raise ValueError
    with pytest.raises(ValueError, match="precondition failed"):
        svd_xf.apply(A_noise)


def test_svd_structured_low_rank_accepted():
    """Verify that matrices with decaying singular spectra (low-rank structure) are accepted."""
    np.random.seed(42)
    # Construct rank-8 matrix
    U = np.random.randn(128, 8).astype(np.float32)
    V = np.random.randn(128, 8).astype(np.float32)
    A_low_rank = U @ V.T

    svd_xf = LowRankSVDTransformation(target_rank=16, min_energy_ratio=0.95)
    valid, msg = svd_xf.check_preconditions(A_low_rank)

    assert valid
    assert msg == "Preconditions satisfied."

    u, s, vt = svd_xf.apply(A_low_rank)
    reconstructed = (u * s) @ vt
    max_err = float(np.max(np.abs(A_low_rank - reconstructed)))
    assert max_err < 1e-4


def test_svd_adaptive_energy_selection():
    """Verify dynamic energy thresholding (sum sigma_i / sum sigma >= 0.99) adapts rank."""
    np.random.seed(42)
    # Construct rank-6 matrix with mild decaying noise
    U = np.random.randn(64, 6).astype(np.float32)
    V = np.random.randn(64, 6).astype(np.float32)
    A_structured = U @ V.T + 1e-4 * np.random.randn(64, 64).astype(np.float32)

    svd_adaptive = LowRankSVDTransformation(
        target_rank=None,
        target_energy_ratio=0.99,
        adaptive_energy_selection=True,
    )
    valid, msg = svd_adaptive.check_preconditions(A_structured)
    assert valid
    assert "Adaptive rank" in msg
    assert svd_adaptive._selected_rank <= 8  # Dynamically chose minimal rank around 6

    u, s, vt = svd_adaptive.apply(A_structured)
    assert u.shape[1] == svd_adaptive._selected_rank
    reconstructed = (u * s) @ vt
    assert np.allclose(A_structured, reconstructed, atol=1e-3)



def test_opencl_task_size_thresholding():
    """Verify that payloads < 256 KB are routed to CPU_AVX2 to avoid command queue latency."""
    scheduler = UniversalScheduler()

    # Case 1: Payload 128 KB (< 256 KB threshold) -> must route to CPU_AVX2
    plan_small = scheduler.schedule_workload("GEMM_STANDARD", data_size_bytes=128 * 1024)
    assert plan_small.selected_backend == "CPU_AVX2"

    # Case 2: Payload 1024 KB (> 256 KB threshold) -> may route to OpenCL if available
    plan_large = scheduler.schedule_workload("GEMM_STANDARD", data_size_bytes=1024 * 1024)
    assert plan_large.selected_backend in ("INTEL_UHD_IGPU_OPENCL", "CPU_AVX2")


def test_double_buffering_prefetch_thresholding():
    """Verify prefetch thresholding: files < 8 MB use sync stream; >= 8 MB use async double-buffering."""
    engine = OutOfCoreStreamEngine()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Case 1: Small file (512 KB < 8 MB)
        small_file = os.path.join(tmpdir, "small.bin")
        data_small = np.ones(128 * 1024, dtype=np.float32)  # 512 KB
        data_small.tofile(small_file)

        res_s, rep_s = engine.stream_double_buffered_file_reduction(small_file, chunk_size_bytes=64 * 1024)
        assert np.isclose(res_s, float(np.sum(data_small)))
        assert "sync_below_8mb" in rep_s.workload_id

        # Case 2: Large file (8.5 MB >= 8 MB)
        large_file = os.path.join(tmpdir, "large.bin")
        # 2,200,000 floats * 4 = 8.8 MB
        data_large = np.ones(2_200_000, dtype=np.float32)
        data_large.tofile(large_file)

        res_l, rep_l = engine.stream_double_buffered_file_reduction(large_file, chunk_size_bytes=1024 * 1024)
        assert np.isclose(res_l, float(np.sum(data_large)))
        assert "async_double_buffered" in rep_l.workload_id


def test_sparse_2_4_structured_kernel():
    """Verify 2:4 structured sparsity pruning, packing, and compiled AVX2 GEMM."""
    np.random.seed(42)
    M, K, N = 64, 128, 32
    W = np.random.randn(M, K).astype(np.float32)
    X = np.random.randn(N, K).astype(np.float32)

    W_packed, indices_packed, W_masked = prune_and_pack_2_4(W)

    # 1. Verify 2:4 property: exactly 2 non-zeros per 4-block
    for m in range(M):
        for b in range(K // 4):
            block = W_masked[m, b * 4 : (b + 1) * 4]
            assert np.count_nonzero(block) == 2

    # 2. Verify AVX2 compiled execution matches masked ground truth
    ref_Y = X @ W_masked.T
    sparse_Y = gemm_2_4_sparse_avx2(X, W_packed, indices_packed)

    max_diff = float(np.max(np.abs(ref_Y - sparse_Y)))
    assert max_diff < 1e-4

    # 3. Benchmark engine verification
    engine = StructuredSparse24Engine(M=64, K=128)
    metrics = engine.benchmark_speedup(N=32, warmup=2, reps=10)
    assert metrics["verified"]
    assert metrics["compression_ratio"] > 1.5


def test_bitnet_ternary_kernel():
    """Verify BitNet 1.58b ternary quantization, pure add/sub GEMM, and zero multipliers."""
    np.random.seed(42)
    M, K, N = 64, 128, 32
    W = np.random.randn(M, K).astype(np.float32)
    X = np.random.randn(N, K).astype(np.float32)

    W_ternary, gamma, packed = quantize_to_bitnet_ternary(W)

    # 1. Verify weights are strictly {-1, 0, +1}
    unique_vals = set(np.unique(W_ternary).tolist())
    assert unique_vals.issubset({-1, 0, 1})

    # 2. Verify compiled AVX2 kernel matches mathematical expectation
    W_reconstructed = (W_ternary * gamma).astype(np.float32)
    ref_Y = X @ W_reconstructed.T
    ternary_Y = bitnet_ternary_gemm_avx2(X, W_ternary, gamma)

    max_diff = float(np.max(np.abs(ref_Y - ternary_Y)))
    assert max_diff < 1e-4

    # 3. Benchmark engine verification
    engine = BitNetTernaryEngine(M=64, K=128)
    metrics = engine.benchmark_speedup(N=32, warmup=2, reps=10)
    assert metrics["verified"]
    assert metrics["multiplication_count"] == 0
    assert metrics["compression_ratio"] >= 10.0
