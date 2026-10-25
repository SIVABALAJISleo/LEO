"""
tests/test_universal_parity_engine.py
======================================
Comprehensive test suite for the Universal Application-Parity Engine (UAPE).

Tests:
1. Spectral / Frequency Domain Convolution Phase Change (FFT vs direct spatial).
2. Low-Rank Subspace Factorization (SVD / LoRA phase change vs dense GEMM).
3. Dynamic Attention Manifold Sparsification (Top-K power-law pruning).
4. Discrete Bitwise Vector Symbolic Architecture (Single-cycle Hamming similarity).
5. Full End-to-End Application-Parity Pipeline with exact semantic caching and self-falsification.
6. Honest Parity Tier Demarcation (RAW_HARDWARE vs CONTRACT vs APPLICATION_PERFORMANCE).
"""

import math
import numpy as np
import pytest

from hyper_phase_change.universal_parity_engine import (
    ParityTier,
    ComputationalPhase,
    ParityExecutionResult,
    UniversalApplicationParityEngine,
    UNIVERSAL_PARITY_ENGINE,
)
from hyper_phase_change.backend_router import ROUTER, ExecutionPolicy


def test_spectral_convolution_phase_change():
    """Verify that FFT frequency domain convolution matches spatial direct convolution."""
    engine = UniversalApplicationParityEngine()
    rng = np.random.default_rng(42)

    x = rng.standard_normal((32, 32)).astype(np.float32)
    kernel = rng.standard_normal((5, 5)).astype(np.float32)

    # 1. Frequency Spectral Phase Change
    fft_out, elapsed_ms = engine.convolve_spectral_phase_change(x, kernel)

    # 2. Independent Reference Direct Spatial Convolution
    H_x, W_x = x.shape
    H_k, W_k = kernel.shape
    out_H = H_x - H_k + 1
    out_W = W_x - W_k + 1
    ref_out = np.zeros((out_H, out_W), dtype=np.float32)
    for i in range(out_H):
        for j in range(out_W):
            ref_out[i, j] = np.sum(x[i : i + H_k, j : j + W_k] * kernel)

    max_diff = float(np.max(np.abs(fft_out - ref_out)))
    assert max_diff < 1e-4, f"FFT convolution output mismatch: max diff {max_diff}"
    assert fft_out.shape == (28, 28)


def test_low_rank_gemm_phase_change():
    """Verify that low-rank SVD factorization replaces O(N^3) with O(2 N r) when rank is low."""
    engine = UniversalApplicationParityEngine()
    rng = np.random.default_rng(101)

    M, K, N = 64, 64, 64
    A = rng.standard_normal((M, K)).astype(np.float32)

    # Construct an intrinsically low-rank matrix B (rank 4)
    U_low = rng.standard_normal((K, 4)).astype(np.float32)
    V_low = rng.standard_normal((4, N)).astype(np.float32)
    B_low_rank = np.matmul(U_low, V_low)

    # Low-rank transformation
    factored_out, rank, elapsed_ms = engine.gemm_low_rank_phase_change(A, B_low_rank, rank_threshold=0.99)
    assert factored_out is not None
    assert rank is not None
    assert rank <= 5

    # Check numerical equivalence against direct dense matmul
    ref_out = np.matmul(A, B_low_rank)
    rel_error = float(np.linalg.norm(factored_out - ref_out) / np.linalg.norm(ref_out))
    assert rel_error < 1e-4

    # Full rank matrix should be rejected by the economic guard (fail-closed)
    B_full_rank = rng.standard_normal((K, N)).astype(np.float32)
    full_factored_out, full_rank, _ = engine.gemm_low_rank_phase_change(A, B_full_rank, rank_threshold=0.85)
    assert full_factored_out is None  # Economic guard properly rejected full rank


def test_dynamic_attention_manifold_sparsification():
    """Verify top-k dynamic power-law pruning in multi-head attention."""
    engine = UniversalApplicationParityEngine()
    rng = np.random.default_rng(202)

    seq_len, d_k = 64, 32
    Q = rng.standard_normal((seq_len, d_k)).astype(np.float32) * 1.5
    K = rng.standard_normal((seq_len, d_k)).astype(np.float32) * 1.5
    V = rng.standard_normal((seq_len, d_k)).astype(np.float32)

    # Dense reference attention
    scale = 1.0 / math.sqrt(d_k)
    scores = np.matmul(Q, K.T) * scale
    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    probs = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    dense_ref = np.matmul(probs, V)

    # Top-50% dynamic sparse attention
    sparse_out, elapsed_ms, sparsity = engine.sparse_attention_phase_change(Q, K, V, keep_ratio=0.50)
    assert sparsity == pytest.approx(0.50, abs=0.05)
    assert sparse_out.shape == (seq_len, d_k)

    # Cosine similarity between sparse projection and dense reference
    dot_prod = np.sum(sparse_out * dense_ref)
    norm_sparse = np.linalg.norm(sparse_out)
    norm_dense = np.linalg.norm(dense_ref)
    cosine_sim = dot_prod / (norm_sparse * norm_dense)
    assert cosine_sim > 0.90, f"Sparse attention deviated from manifold direction: {cosine_sim}"


def test_discrete_bitwise_vsa_similarity():
    """Verify single-cycle bitwise Hamming distance similarity over packed words."""
    engine = UniversalApplicationParityEngine()
    rng = np.random.default_rng(303)

    # 10,000-bit hyperdimensional vector codebook (10 entries)
    dim_bits = 64 * 10  # 640 bits
    codebook = (rng.uniform(-1.0, 1.0, size=(10, dim_bits)) > 0).astype(np.float32)

    # Create a query vector identical to entry 4 with small 5% noise
    query = codebook[4].copy()
    noise_idx = rng.choice(dim_bits, size=int(dim_bits * 0.05), replace=False)
    query[noise_idx] = 1.0 - query[noise_idx]

    best_idx, elapsed_ms = engine.bitwise_vsa_similarity(query, codebook)
    assert best_idx == 4, f"Bitwise VSA failed to retrieve closest associative memory anchor: got {best_idx}"
    assert elapsed_ms >= 0.0


def test_end_to_end_application_parity_execution():
    """Verify full pipeline execution, honest device attribution, and exact memoization."""
    engine = UniversalApplicationParityEngine()
    rng = np.random.default_rng(404)

    inputs = {
        "image": rng.standard_normal((64, 64)).astype(np.float32),
        "kernel": rng.standard_normal((5, 5)).astype(np.float32),
    }

    # 1. Cold execution via Frequency Spectral Phase Change
    res1 = engine.execute_with_application_parity("CONV2D_STANDARD", inputs)
    assert res1.is_verified is True
    assert res1.achieved_tier in (ParityTier.APPLICATION_PERFORMANCE_PARITY, ParityTier.CONTRACT_PARITY)
    assert res1.selected_phase == ComputationalPhase.FREQUENCY_SPECTRAL
    assert "AVX2" in res1.hardware_attribution or "CPU" in res1.hardware_attribution
    assert res1.self_falsification_passed is True

    # 2. Warm execution via Exact Semantic Manifold Caching
    res2 = engine.execute_with_application_parity("CONV2D_STANDARD", inputs)
    assert res2.is_verified is True
    assert res2.selected_phase == ComputationalPhase.EXACT_MANIFOLD_REUSE
    assert res2.redundant_flops_eliminated == 1.0
    assert "Exact Semantic Cache" in res2.hardware_attribution
    np.testing.assert_allclose(res1.output, res2.output)


def test_honest_parity_demarcation():
    """Verify that RAW_HARDWARE_PARITY is never claimed, upholding scientific truth."""
    res = UNIVERSAL_PARITY_ENGINE.execute_with_application_parity(
        "SORT_STANDARD",
        {"x": np.array([5.0, 2.0, 8.0, 1.0], dtype=np.float32)},
    )
    # RAW_HARDWARE_PARITY must never be the achieved tier
    assert res.achieved_tier != ParityTier.RAW_HARDWARE_PARITY
    assert res.achieved_tier in (ParityTier.CONTRACT_PARITY, ParityTier.APPLICATION_PERFORMANCE_PARITY)
    assert "Intel" in res.hardware_attribution
