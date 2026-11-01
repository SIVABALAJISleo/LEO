"""
tests/test_universal_100_contract_closure.py
============================================
Automated Falsification & Contract Parity Test Suite for the Six Universal Closures.

Tests:
  1. QuIP# FWHT 2-bit quantization on outlier-heavy weights: >= 2.5x error reduction vs naive ternary,
     and auto-promotion to 4-bit / fallback when tolerance is tightened to 1e-3.
  2. Chebyshev matrix operator exponential action: <= 1e-4 relative error vs exact eigh,
     and exact fallback triggering when contract tolerance is violated.
  3. Lookahead Async NVMe double-buffering: prefetch hit with cos_sim >= 0.85 and max_dev <= 1e-5;
     adversarial orthogonal shock strictly triggers synchronous re-fetch fallback.
  4. Ragged continuous batching vs static 2D padding: exact numerical equivalence (deviation <= 1e-6),
     and >= 7.0x KV-cache byte compression.
  5. 1982 Oja Subspace MeZO: lower final loss than isotropic MeZO within equal step budget,
     with strictly 0 activation graph bytes.
  6. Quasi-Monte Carlo (Halton) + Control Variate: >= 10x error reduction vs standard MC at N = 512.
"""

import numpy as np
import pytest

from backend.canonical.universal_100_contract_closure import (
    fwht_inplace,
    hadamard_incoherent_2bit_gemv,
    chebyshev_matrix_exp_action,
    benchmark_lookahead_async_nvme_pipeline,
    benchmark_ragged_continuous_batch_and_kv_compression,
    benchmark_subspace_mezo_galore_training,
    benchmark_qmc_control_variate_subsumption,
)
from backend.canonical.native_runtime_bridge import NativeRuntimeBridge


def test_1_fwht_incoherence_and_autopromotion():
    """
    Asserts FWHT reduces 2-bit quantization error by >= 2.5x on outlier-contaminated weights,
    and auto-promotes when contract tolerance is tightened to 1e-3.
    """
    rng = np.random.default_rng(42)
    M, K = 64, 64
    W = rng.standard_normal((M, K)).astype(np.float32)
    # Contaminate 2 channels with heavy outliers (kurtosis > 20x)
    W[:, [7, 29]] *= 60.0
    x = rng.standard_normal(K).astype(np.float32)

    # 1. Naive Ternary Quantization Error (without Hadamard rotation)
    y_exact = W @ x
    scales = np.mean(np.abs(W), axis=1, keepdims=True) * 1.5
    W_naive_ternary = np.sign(W) * scales
    y_naive = W_naive_ternary @ x
    naive_err = float(np.linalg.norm(y_naive - y_exact) / (np.linalg.norm(y_exact) + 1e-12))

    # 2. QuIP# Hadamard Incoherent 2-Bit Quantization
    bridge = NativeRuntimeBridge()
    res_pos = hadamard_incoherent_2bit_gemv(W, x, contract_tol=0.25, native_bridge=bridge)

    assert res_pos.status == "PASS"
    assert res_pos.executed_mode == "HADAMARD_INCOHERENT_2BIT"
    assert res_pos.kurtosis_ratio > 15.0

    # Assert error reduction ratio >= 2.5x
    error_reduction = float(naive_err / max(res_pos.contract_error, 1e-12))
    assert error_reduction >= 2.5, f"Expected >= 2.5x error reduction, got {error_reduction:.2f}x"

    # 3. Tightened Contract Tolerance -> Auto-promotion to 4-bit / fallback
    res_tight = hadamard_incoherent_2bit_gemv(W, x, contract_tol=1e-3, native_bridge=bridge)
    assert res_tight.promoted_to_4bit is True
    assert res_tight.executed_mode in ("AUTOPROMOTED_4BIT_CONTRACT", "FALLBACK_EXACT")


def test_2_chebyshev_matrix_exp_action():
    """
    Asserts Chebyshev recurrence operator exponential action matches exact diagonalization
    within <= 1e-4 relative error, and triggers fallback if tolerance is violated.
    """
    rng = np.random.default_rng(101)
    N = 64
    B = rng.standard_normal((N, N)).astype(np.float32)
    A = (B.T @ B) / float(N)  # Symmetric positive semi-definite
    V = rng.standard_normal(N).astype(np.float32)
    V /= float(np.linalg.norm(V))

    # Positive test: degree 24, tol 1e-4
    res_pos = chebyshev_matrix_exp_action(A, V, t=0.5, degree=24, contract_tol=1e-4)
    assert res_pos.status == "PASS"
    assert res_pos.executed_mode == "CHEBYSHEV_RECURRENCE_ACCELERATED"
    assert res_pos.relative_error <= 1e-4
    assert res_pos.fallback_triggered is False

    # Adversarial fallback test: degree 3 with strict tolerance 1e-8
    res_adv = chebyshev_matrix_exp_action(A, V, t=0.5, degree=3, contract_tol=1e-8)
    assert res_adv.status == "PASS"
    assert res_adv.fallback_triggered is True
    assert res_adv.executed_mode == "FALLBACK_EXACT_EIGH"


def test_3_lookahead_async_nvme_pipeline():
    """
    Asserts Lookahead Async NVMe pipeline matches synchronous output within <= 1e-5,
    and triggers synchronous re-fetch fallback when adversarial orthogonal shock is injected.
    """
    rng = np.random.default_rng(202)
    d_in = 64
    hot_count = 16
    cold_count = 128
    rank_r = 8

    layer_weights = [
        {"hot_weights": rng.standard_normal((hot_count, d_in)).astype(np.float32)},
        {
            "cold_store": rng.standard_normal((cold_count, d_in)).astype(np.float32),
            "sketch_right": rng.standard_normal((rank_r, d_in)).astype(np.float32),
            "sketch_left": rng.standard_normal((cold_count, rank_r)).astype(np.float32),
        },
    ]
    input_batch = rng.standard_normal((4, d_in)).astype(np.float32)

    # 1. Positive run: Natural residual stream lookahead
    res_pos = benchmark_lookahead_async_nvme_pipeline(
        layer_weights, input_batch, adversarial_shock=False, similarity_threshold=0.85
    )
    assert res_pos.status == "PASS"
    assert res_pos.prefetch_hit is True
    assert res_pos.executed_mode == "ASYNC_LOOKAHEAD_PREFETCH_OVERLAPPED"
    assert res_pos.cos_similarity >= 0.85
    assert res_pos.max_relative_deviation <= 1e-5

    # 2. Adversarial run: Orthogonal representation shock
    res_adv = benchmark_lookahead_async_nvme_pipeline(
        layer_weights, input_batch, adversarial_shock=True, similarity_threshold=0.85
    )
    assert res_adv.status == "PASS"
    assert res_adv.prefetch_hit is False
    assert res_adv.executed_mode == "SYNCHRONOUS_REFETCH_FALLBACK"
    assert res_adv.cos_similarity < 0.85


def test_4_ragged_continuous_batching_and_kv_compression():
    """
    Asserts Ragged Continuous Batching matches static padded batching within <= 1e-6
    on real tokens while achieving >= 7.0x KV-cache byte compression.
    """
    rng = np.random.default_rng(303)
    D_in = 64
    D_out = 64
    weights = (rng.standard_normal((D_out, D_in)) / np.sqrt(D_in)).astype(np.float32)

    # Multi-user requests of varied lengths (LayerNorm normalized inputs)
    seq_lens = [5, 27, 48, 12, 33]
    requests = [(rng.standard_normal((t_len, D_in)) / np.sqrt(D_in)).astype(np.float32) for t_len in seq_lens]

    res = benchmark_ragged_continuous_batch_and_kv_compression(requests, weights, page_size=16)

    assert res.status == "PASS"
    assert res.max_deviation <= 1e-6, f"Expected deviation <= 1e-6, got {res.max_deviation}"
    assert res.padding_flops_eliminated_pct > 20.0
    assert res.kv_compression_ratio >= 7.0, f"Expected >= 7.0x compression, got {res.kv_compression_ratio}x"


def test_5_subspace_mezo_galore_training():
    """
    Asserts Oja Subspace MeZO achieves lower final loss than isotropic MeZO in the same step budget
    with strictly 0 activation graph bytes.
    """
    rng = np.random.default_rng(404)
    d_out, d_in = 16, 32
    W_init = rng.standard_normal((d_out, d_in)).astype(np.float32)

    # Generate streaming regression dataset with low-rank latent structure
    n_samples = 150
    U_true = rng.standard_normal((d_in, 4)).astype(np.float32)
    X_stream = (rng.standard_normal((n_samples, 4)) @ U_true.T).astype(np.float32)
    W_target = rng.standard_normal((d_out, d_in)).astype(np.float32)
    y_stream = (X_stream @ W_target.T).astype(np.float32)

    res = benchmark_subspace_mezo_galore_training(
        weights=W_init,
        X_stream=X_stream,
        y_stream=y_stream,
        rank_r=4,
        steps=50,
    )

    assert res.status == "PASS"
    assert res.stored_activation_bytes == 0
    assert res.subspace_final_loss < res.isotropic_final_loss, (
        f"Subspace loss {res.subspace_final_loss} should be < isotropic {res.isotropic_final_loss}"
    )
    assert res.subspace_variance_reduction_factor >= 2.0


def test_6_qmc_halton_control_variate():
    """
    Asserts Quasi-Monte Carlo (Halton) + Control Variate achieves >= 10x lower
    integration error than standard pseudo-random Monte Carlo at N = 512 samples.
    """
    res = benchmark_qmc_control_variate_subsumption(N=512, d=2, seed=42)

    assert res.status == "PASS"
    assert res.samples == 512
    assert res.qmc_cv_error < res.mc_error
    assert res.measured_error_reduction_factor >= 10.0, (
        f"Expected >= 10x error reduction, got {res.measured_error_reduction_factor:.2f}x"
    )
