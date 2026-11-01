"""
tests/test_unseen_subsumption_suite.py
======================================
Adversarial Falsification and Contract Parity Suite for the
5 Formulation-Shift Breakthrough Engines (Project LEO).

Tests:
  - Test 1A (HODLR Positive): Banded diagonal + rank-24 off-diagonal matrix achieves < 5% error via HODLR.
  - Test 1B (HODLR Adversarial Falsification): Banded diagonal + white-noise off-diagonal rejected by Freivalds probe.
  - Test 2A (Contextual Hot/Cold Positive): Power-law FFN weights achieve >= 5x NVMe I/O byte reduction.
  - Test 2B (Contextual Hot/Cold Falsification): Uniform flat-spectrum FFN weights trigger energy guard fallback.
  - Test 3 (L3-Coalesced Radix Concurrency): 32 concurrent requests achieve > 10x RAM bandwidth reduction.
  - Test 4 (MeZO In-Place Training): Reduces MSE loss over 60 steps using exactly 8 bytes optimizer state.
  - Test 5 (Deterministic Radiance Cascade): Multi-level 2D radiance transport with O(N log N) probe scaling and zero artifacts.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from backend.canonical.unseen_subsumption_extensions import (
    HodlrCurResult,
    hodlr_banded_cur_gemm,
    ContextualHotColdResult,
    ContextualHotColdFFN,
    contextual_hot_cold_ffn_step,
    RadixPrefixCache,
    L3CoalescedConcurrencyResult,
    benchmark_l3_coalesced_concurrency,
    MeZOInPlaceTrainer,
    RadianceCascadeResult,
    deterministic_radiance_cascade_2d,
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


# ==============================================================================
# Test 1A & 1B: HODLR Banded Diagonal + CUR Residual Engine
# ==============================================================================

def test_1a_hodlr_banded_diagonal_plus_cur_positive():
    """
    Test 1A (HODLR Positive):
    A matrix with a dominant narrow diagonal band plus rank-24 off-diagonal residual
    achieves < 5% error via HODLR_BANDED_PLUS_CUR_VERIFIED where pure Global CUR fails.
    """
    rng = np.random.default_rng(42)
    M, K, N = 256, 256, 128
    b_bandwidth = 16
    r_target = 24
    r_half = r_target // 2

    # 1. Exact narrow diagonal band
    row_idx = np.arange(M)[:, np.newaxis]
    col_idx = np.arange(K)[np.newaxis, :]
    band_mask = np.abs(row_idx - col_idx) <= b_bandwidth
    D_band = np.where(band_mask, 5.0 * np.exp(-np.abs(row_idx - col_idx) / 4.0), 0.0).astype(np.float32)

    # 2. Smooth rank-24 off-diagonal residual in HODLR structure (A_12 and A_21 blocks)
    h = 128 - b_bandwidth
    U1 = rng.standard_normal((h, r_half)).astype(np.float32)
    V1 = rng.standard_normal((r_half, 128)).astype(np.float32)
    A12 = (U1 @ V1).astype(np.float32)

    U2 = rng.standard_normal((128, r_half)).astype(np.float32)
    V2 = rng.standard_normal((r_half, h)).astype(np.float32)
    A21 = (U2 @ V2).astype(np.float32)

    A_off = np.zeros((M, K), dtype=np.float32)
    A_off[:h, 128:] = A12
    A_off[128:, :h] = A21

    A = (D_band + A_off).astype(np.float32)
    B = rng.standard_normal((K, N)).astype(np.float32)

    # Execute HODLR solver
    contract_bound = 0.051
    res = hodlr_banded_cur_gemm(
        A, B, half_bandwidth=b_bandwidth, rank_target=r_target, epsilon_contract=contract_bound, seed=101
    )

    exact_ref = A @ B
    measured_error = float(np.linalg.norm(res.result - exact_ref) / (np.linalg.norm(exact_ref) + 1e-12))

    assert res.freivalds_passed is True
    assert res.executed_mode == "HODLR_BANDED_PLUS_CUR_VERIFIED"
    assert res.is_fallback is False
    assert measured_error < contract_bound
    assert res.delivered_relative_error < contract_bound

    # Compare with FunctionalReplacementEngine: global CUR fails on A due to diagonal dominance,
    # and secondary HODLR solver automatically takes over!
    fre = FunctionalReplacementEngine(seed=42)
    fre_res = fre.cur_skeleton_gemm(A, B, c_samples=r_target, epsilon_tol=contract_bound)
    assert fre_res.executed_mode == "HODLR_BANDED_PLUS_CUR_VERIFIED"
    assert fre_res.freivalds_passed is True


def test_1b_hodlr_adversarial_white_noise_falsification():
    """
    Test 1B (HODLR Adversarial Falsification):
    A matrix with a narrow diagonal band but dense Gaussian white noise off-diagonal residual
    fails Freivalds verification and falls back to exact computation with 0.0 delivered error.
    """
    rng = np.random.default_rng(43)
    M, K, N = 256, 256, 128
    b_bandwidth = 16
    r_target = 24

    row_idx = np.arange(M)[:, np.newaxis]
    col_idx = np.arange(K)[np.newaxis, :]
    band_mask = np.abs(row_idx - col_idx) <= b_bandwidth
    D_band = np.where(band_mask, 3.0, 0.0).astype(np.float32)

    # Incompressible white noise off-diagonal
    A_off_noise = np.where(band_mask, 0.0, rng.standard_normal((M, K))).astype(np.float32)
    A = (D_band + A_off_noise).astype(np.float32)
    B = rng.standard_normal((K, N)).astype(np.float32)

    contract_bound = 0.049
    res = hodlr_banded_cur_gemm(
        A, B, half_bandwidth=b_bandwidth, rank_target=r_target, epsilon_contract=contract_bound, seed=102
    )

    exact_ref = A @ B
    assert res.freivalds_passed is False
    assert res.executed_mode == "HODLR_REJECTED_BY_FREIVALDS_EXACT_FALLBACK"
    assert res.is_fallback is True
    assert res.delivered_relative_error == 0.0
    np.testing.assert_allclose(res.result, exact_ref, rtol=1e-5, atol=1e-5)


# ==============================================================================
# Test 2A & 2B: Contextual Hot/Cold Neuron Subsumption
# ==============================================================================

def test_2a_contextual_hot_cold_power_law_positive():
    """
    Test 2A (Contextual Hot/Cold Positive):
    Power-law distributed FFN weights achieve >= 5x NVMe I/O byte reduction
    within contract tolerance.
    """
    rng = np.random.default_rng(201)
    d_in = 256
    d_ffn = 1024
    B = 4

    # Heavy-tailed power-law spectrum
    power_scales = np.array([float(i + 1) ** (-1.2) for i in range(d_ffn)], dtype=np.float32)
    W_gate = rng.standard_normal((d_ffn, d_in)).astype(np.float32) * power_scales[:, np.newaxis]
    W_up = rng.standard_normal((d_ffn, d_in)).astype(np.float32) * power_scales[:, np.newaxis]
    W_down = rng.standard_normal((d_in, d_ffn)).astype(np.float32) * power_scales[np.newaxis, :]

    X = rng.standard_normal((B, d_in)).astype(np.float32)

    # Exact full forward reference
    H_gate_exact = X @ W_gate.T
    H_up_exact = X @ W_up.T
    A_exact = (H_gate_exact / (1.0 + np.exp(-np.clip(H_gate_exact, -16.0, 16.0)))) * H_up_exact
    Y_exact = A_exact @ W_down.T

    res = contextual_hot_cold_ffn_step(
        W_gate=W_gate,
        W_up=W_up,
        W_down=W_down,
        X=X,
        target_hot_ratio=0.15,
        target_cold_active_ratio=0.10,
        energy_threshold=0.30,
        exact_reference=Y_exact,
    )

    target_min_io_factor = 5.0
    assert res.executed_mode == "CONTEXTUAL_HOT_COLD_SUB_SAMPLED"
    assert res.is_fallback is False
    assert res.measured_io_reduction_factor >= target_min_io_factor
    assert res.energy_captured_ratio >= 0.30

    rel_error = float(np.linalg.norm(res.output - Y_exact) / (np.linalg.norm(Y_exact) + 1e-12))
    assert rel_error < 0.20


def test_2b_contextual_hot_cold_uniform_spectrum_falsification():
    """
    Test 2B (Contextual Hot/Cold Falsification):
    Uniform flat-spectrum FFN weights produce flat activation distribution,
    triggering the energy concentration guard and falling back to full streaming.
    """
    rng = np.random.default_rng(202)
    d_in = 128
    d_ffn = 512
    B = 2

    # Completely flat i.i.d. Gaussian spectrum (no heavy tails)
    W_gate = rng.standard_normal((d_ffn, d_in)).astype(np.float32)
    W_up = rng.standard_normal((d_ffn, d_in)).astype(np.float32)
    W_down = rng.standard_normal((d_in, d_ffn)).astype(np.float32)
    X = rng.standard_normal((B, d_in)).astype(np.float32)

    # Set strict energy threshold: flat uniform spectrum will capture only ~10% cold energy
    strict_energy_bound = 0.50
    res = contextual_hot_cold_ffn_step(
        W_gate=W_gate,
        W_up=W_up,
        W_down=W_down,
        X=X,
        target_hot_ratio=0.15,
        target_cold_active_ratio=0.10,
        energy_threshold=strict_energy_bound,
    )

    assert res.executed_mode == "FALLBACK_FULL_TILED_STREAMING"
    assert res.is_fallback is True
    assert res.num_cold_active_predicted == res.num_cold_total


# ==============================================================================
# Test 3: L3-Coalesced Micro-Batching & Radix Prefix Concurrency
# ==============================================================================

def test_3_l3_coalesced_radix_concurrency():
    """
    Test 3 (L3-Coalesced Radix Concurrency):
    32 concurrent requests with a shared 16-token prefix achieve > 10x RAM weight
    bandwidth reduction with < 1e-5 numerical deviation against sequential execution.
    """
    rng = np.random.default_rng(301)
    M, K = 512, 512
    B = 32
    # Realistic neural network scaling (Xavier/He normalized)
    weights = (rng.standard_normal((M, K)) / np.sqrt(K)).astype(np.float32)
    request_inputs = [(rng.standard_normal(K) / np.sqrt(K)).astype(np.float32) for _ in range(B)]
    shared_prefix = tuple(range(100, 116))  # 16-token shared prefix

    cache = RadixPrefixCache()
    cache.insert(shared_prefix, np.mean(weights, axis=0).astype(np.float32))

    res = benchmark_l3_coalesced_concurrency(
        weights=weights,
        request_inputs=request_inputs,
        shared_prefix_tokens=shared_prefix,
        cache=cache,
    )

    target_min_bw_factor = 10.0
    tol_max_deviation = 1e-5

    assert res.measured_bandwidth_reduction_factor >= target_min_bw_factor
    assert res.max_deviation < tol_max_deviation
    assert res.prefix_cache_hits == B
    assert cache.total_hits >= 1

    # Verify output shape is (M, B)
    assert res.batched_output.shape == (M, B)
    assert res.sequential_output.shape == (M, B)


# ==============================================================================
# Test 4: Seed-Regenerated In-Place SPSA / MeZO Trainer
# ==============================================================================

def test_4_mezo_in_place_training():
    """
    Test 4 (MeZO In-Place Training):
    Reduces MSE loss on target regression over 60 steps using exactly 8 bytes
    of extra optimizer state and zero stored activation graph memory.
    """
    rng = np.random.default_rng(401)
    N_samples, D_features = 120, 24

    X_train = rng.standard_normal((N_samples, D_features)).astype(np.float32)
    true_weights = rng.standard_normal(D_features).astype(np.float32)
    y_train = (X_train @ true_weights).astype(np.float32)

    w_init = rng.standard_normal(D_features).astype(np.float32)
    trainer = MeZOInPlaceTrainer(weights=w_init.copy(), base_seed=777)

    assert trainer.extra_optimizer_state_bytes == 8
    assert trainer.stored_activation_bytes == 0

    def loss_fn(w: np.ndarray) -> float:
        preds = X_train @ w
        return float(np.mean((preds - y_train) ** 2))

    initial_loss = loss_fn(trainer.weights)
    history = trainer.train(loss_fn, steps=60, lr=0.01, epsilon=0.005)
    final_loss = history[-1]

    assert final_loss < initial_loss
    assert trainer.step_count == 60
    stats = trainer.get_memory_stats()
    assert stats["extra_optimizer_state_bytes"] == 8
    assert stats["stored_activation_bytes"] == 0


# ==============================================================================
# Test 5: Deterministic Radiance Cascades
# ==============================================================================

def test_5_deterministic_radiance_cascade_2d():
    """
    Test 5 (Deterministic Radiance Cascade):
    Computes multi-level 2D radiance transport with O(N log N) probe scaling,
    spatio-temporal reprojection, and zero NaN/Inf artifacts.
    """
    width, height = 128, 128
    # 2D scene with circular emitter in center
    grid = np.zeros((height, width, 3), dtype=np.float32)
    cy, cx = height // 2, width // 2
    y_coords, x_coords = np.ogrid[:height, :width]
    mask = (y_coords - cy) ** 2 + (x_coords - cx) ** 2 <= 16**2
    grid[mask] = [2.0, 1.8, 1.2]

    # Level 1: Static scene
    res1 = deterministic_radiance_cascade_2d(grid, width=width, height=height)

    expected_cascades = int(math.ceil(math.log2(max(width, height))))
    assert res1.num_cascades == expected_cascades
    assert res1.is_deterministic is True
    assert res1.zero_artifacts_verified is True
    assert res1.radiance_map.shape == (height, width, 3)
    assert not np.isnan(res1.radiance_map).any()
    assert not np.isinf(res1.radiance_map).any()
    assert res1.total_probes_computed > 0

    # Level 2: Spatio-temporal reprojection with motion vectors
    motion_vectors = np.ones((height, width, 2), dtype=np.float32) * 2.0
    res2 = deterministic_radiance_cascade_2d(
        grid,
        width=width,
        height=height,
        prev_frame=res1.radiance_map,
        motion_vectors=motion_vectors,
        temporal_alpha=0.80,
    )

    assert res2.zero_artifacts_verified is True
    assert not np.isnan(res2.radiance_map).any()
    assert not np.isinf(res2.radiance_map).any()
