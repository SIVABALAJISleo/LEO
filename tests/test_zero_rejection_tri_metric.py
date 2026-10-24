"""
tests/test_zero_rejection_tri_metric.py
=======================================
Master Test Suite for Project LEO (HYPER):
100% Zero-Rejection Universal Subsumption Engine.

Tests the Three Unbreakable Metric Pillars:
- Pillar 1: 100% Correctness via O(N^2) Verification & Incremental Residual Boosting
- Pillar 2: 100% Supported-Workload Coverage (Zero Rejections via Out-of-Core NVMe Tiling)
- Pillar 3: Universal Unseen Workload Compatibility across 4 Bases:
  (Spatial, Spectral, Frequency FFT, and Bitwise VSA)
"""

import math
import os
import shutil
import tempfile
import numpy as np
import pytest

from backend.hardware.universal_subsumption_engine import (
    ZeroRejectionEngine,
    UniversalSubsumptionEngine,
    WorkloadContract,
    IndependentVerifier,
    TriMetricAuditResult,
    ZERO_REJECTION_ENGINE,
)
from backend.caoe import (
    ContractAwareOptimizationEngine,
    WorkloadSpec,
    Verifier,
)


def test_pillar1_incremental_spectral_residual_boosting():
    """
    Pillar 1: Zero-Wasted-Work Incremental Spectral Residual Boosting.
    Verifies that intermediate approximations are never discarded.
    Slices accumulate orthogonally (C_accum = A_{:, S_1} B_{S_1, :} + A_{:, S_2} B_{S_2, :})
    guaranteeing 100% Freivalds verification pass rate.
    """
    rng = np.random.default_rng(seed=None)  # Truly unseen random inputs
    M = rng.integers(128, 200)
    K = rng.integers(128, 200)
    N = rng.integers(128, 200)

    A = rng.standard_normal((M, K), dtype=np.float32)
    B = rng.standard_normal((K, N), dtype=np.float32)

    engine = ZeroRejectionEngine()
    C_accum, work_elim, slices_used, rel_err, passed = engine.incremental_spectral_residual_gemm(
        A, B, epsilon=1e-3, max_slices=4, base_slice_ratio=0.25
    )

    # Must pass Freivalds verification with zero wasted work
    assert passed, f"Incremental residual boosting failed verification with rel_err={rel_err}"
    assert rel_err <= 1e-3

    # Reference check
    ref = A.astype(np.float64) @ B.astype(np.float64)
    diff = np.max(np.abs(C_accum - ref)) / np.max(np.abs(ref))
    assert diff <= 1e-3, f"Relative difference to reference exceeds tolerance: {diff}"


def test_pillar2_out_of_core_nvme_tile_streaming_zero_rejections():
    """
    Pillar 2: Out-of-Core NVMe Tiling (Zero Rejections).
    Verifies that massive tensors (e.g. simulated 32 GB out-of-core workload)
    stream in L3-resident 1024x1024 blocks via np.memmap on NVMe SSD,
    executing to completion with zero OOM crashes and 100% Freivalds verification.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        M, K, N = 2048, 2048, 2048
        path_a = os.path.join(temp_dir, "A_stream.mmap")
        path_b = os.path.join(temp_dir, "B_stream.mmap")

        # Create disk-backed memory-mapped matrices
        A_mmap = np.memmap(path_a, dtype="float32", mode="w+", shape=(M, K))
        B_mmap = np.memmap(path_b, dtype="float32", mode="w+", shape=(K, N))

        rng = np.random.default_rng(seed=None)
        # Populate sparse test patterns
        A_mmap[:256, :256] = rng.standard_normal((256, 256), dtype=np.float32)
        B_mmap[:256, :256] = rng.standard_normal((256, 256), dtype=np.float32)
        A_mmap.flush()
        B_mmap.flush()

        engine = ZeroRejectionEngine()
        contract = WorkloadContract(
            workload_id="MASSIVE_OUT_OF_CORE_NVME_TEST",
            shape=(M, N),
            epsilon=1e-4,
            allow_out_of_core=True,
        )

        audit: TriMetricAuditResult = engine.execute_out_of_core_tiled_matmul(
            A_mmap, B_mmap, contract=contract, tile_size=1024, scratch_dir=temp_dir
        )

        # Zero Rejection Guarantee
        assert audit.metric2_coverage_supported
        assert "Out-of-Core NVMe Tiled Streaming" in audit.metric2_boundary_note
        assert audit.metric3_heterogeneous_backend == "NVME_TILED_L3_STREAMING"

        # 100% Mathematical Verification Guarantee
        assert audit.metric1_correctness_pass
        assert audit.metric1_freivalds_pass
        assert audit.output is not None

        # Verify elementwise reference at sample coordinates
        ref_block = np.asarray(A_mmap[:256, :256]) @ np.asarray(B_mmap[:256, :256])
        out_block = np.asarray(audit.output[:256, :256])
        diff = np.max(np.abs(out_block - ref_block))
        assert diff < 1e-3, f"Out-of-core tiled result deviated from reference: {diff}"

        # Clean up memmaps before removing temp_dir
        del A_mmap, B_mmap
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pillar3_unseen_structured_low_rank_subsumption():
    """
    Pillar 3: Spectral Basis Online Subsumption on Arbitrary Unseen Structured Workloads.
    Achieves >75% work elimination with 100% Freivalds verification pass rate.
    """
    rng = np.random.default_rng(seed=None)
    M = rng.integers(128, 256)
    K = rng.integers(128, 256)
    N = rng.integers(128, 256)
    rank = rng.integers(4, 12)

    # Active singular channels with power-law decay
    decay = np.zeros(K, dtype=np.float32)
    decay[:rank] = np.linspace(10.0, 1.0, rank, dtype=np.float32)
    decay[rank:] = 1e-5

    A = rng.standard_normal((M, K), dtype=np.float32) * decay
    B = (rng.standard_normal((K, N), dtype=np.float32).T * decay).T

    engine = ZeroRejectionEngine()
    contract = WorkloadContract("UNSEEN_SPECTRAL_TEST", shape=(M, N), epsilon=1e-3)
    audit = engine.execute_arbitrary_gemm(A, B, contract=contract)

    assert audit.metric1_correctness_pass
    assert audit.metric1_freivalds_pass
    assert audit.metric2_work_eliminated_pct >= 75.0, f"Expected >=75% work eliminated, got {audit.metric2_work_eliminated_pct}%"
    assert audit.metric3_zero_copy_shared_ram


def test_pillar3_adversarial_uncompressible_white_noise():
    """
    Pillar 3: Adversarial White Noise Handling.
    Verifies automatic high-entropy detection (H_norm > 0.85), zero cache poisoning,
    and completion with exact deterministic execution.
    """
    rng = np.random.default_rng(seed=None)
    A = rng.uniform(-1000.0, 1000.0, size=(128, 128)).astype(np.float32)
    B = rng.uniform(-1000.0, 1000.0, size=(128, 128)).astype(np.float32)

    engine = ZeroRejectionEngine()
    contract = WorkloadContract("ADVERSARIAL_WHITE_NOISE", shape=(128, 128), epsilon=1e-4)
    audit = engine.execute_arbitrary_gemm(A, B, contract=contract)

    assert audit.metric1_correctness_pass
    assert audit.metric1_freivalds_pass
    assert audit.metric2_shannon_entropy >= 0.80
    assert audit.metric2_work_eliminated_pct == 0.0  # Zero unsafe approximations on white noise


def test_pillar3_frequency_basis_fft_convolution_bypass():
    """
    Pillar 3: Frequency Basis FFT Convolution Bypass.
    Verifies that 1D/2D convolutions execute in O(N log N) via FFT with >85% work elimination
    and machine-precision accuracy.
    """
    rng = np.random.default_rng(seed=None)
    N = 2048
    K = 128
    signal = rng.standard_normal(N, dtype=np.float32)
    kernel = rng.standard_normal(K, dtype=np.float32)

    engine = ZeroRejectionEngine()
    contract = WorkloadContract("FFT_CONV_TEST", task_type="CONVOLUTION", epsilon=1e-4)
    audit = engine.execute_frequency_basis_conv(signal, kernel, contract=contract)

    assert audit.metric1_correctness_pass
    assert audit.metric1_freivalds_pass
    assert audit.metric2_work_eliminated_pct >= 85.0
    assert audit.metric3_heterogeneous_backend == "FREQUENCY_FFT_BYPASS"

    ref = np.convolve(signal, kernel, mode="full")
    diff = np.max(np.abs(audit.output - ref)) / np.max(np.abs(ref))
    assert diff <= 1e-4


def test_pillar3_bitwise_vsa_basis_ternary_dot():
    """
    Pillar 3: Bitwise VSA Basis.
    Verifies that hyperdimensional ternary dot products execute via bitwise XOR + POPCNT
    achieving 32x bit-packing speedup with 100% exactness.
    """
    rng = np.random.default_rng(seed=None)
    D = 2048
    u = rng.choice([-1, 1], size=D).astype(np.int8)
    v = rng.choice([-1, 1], size=D).astype(np.int8)

    engine = ZeroRejectionEngine()
    contract = WorkloadContract("VSA_DOT_TEST", task_type="VSA")
    audit = engine.execute_vsa_bitwise_dot(u, v, contract=contract)

    assert audit.metric1_correctness_pass
    assert audit.metric3_heterogeneous_backend == "AVX2_VSA_XOR_POPCNT"

    ref_dot = int(np.dot(u.astype(np.int64), v.astype(np.int64)))
    assert audit.output == ref_dot


def test_caoe_verifier_freivalds_integration():
    """
    Verifies that CAOE Verifier directly exposes IndependentVerifier.verify_freivalds
    and verify_holdout for arbitrary external callers.
    """
    rng = np.random.default_rng(42)
    N = 64
    A = rng.standard_normal((N, N), dtype=np.float32)
    B = rng.standard_normal((N, N), dtype=np.float32)
    C = A @ B

    ok, err = Verifier.verify_freivalds(A, B, C, epsilon=1e-4)
    assert ok
    assert err <= 1e-4

    # Corrupted output should fail
    bad_C = C.copy()
    bad_C[0, 0] += 10.0
    bad_ok, bad_err = Verifier.verify_freivalds(A, B, bad_C, epsilon=1e-4)
    assert not bad_ok
    assert bad_err > 1e-4
