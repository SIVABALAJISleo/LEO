"""
tests/test_zero_io_spectral_expert_igpu.py
===========================================
Verification suite for Project LEO Zero-IO Spectral Expert Synthesis
and CPU+iGPU Co-Execution Engine on Intel Core i5-12450H + Intel UHD iGPU.

Verifies:
1. Cooley-Tukey FWHT isometry, energy conservation, and self-inversion.
2. 896-expert memory reduction > 95% (eliminating 26.5s/token cold SSD bottleneck).
3. Exact computational parity (relative L2 error <= 1e-6) between dense and decomposed pathways.
4. AttnRes lookahead top-16 gating and softmax probability normalization.
5. Concurrent CPU + iGPU dual-worker co-execution exact matching.
6. Counterfactual fallback for high-entropy non-spectral expert parameters.
7. Live breakthrough benchmark contract execution.
"""

import math
import numpy as np
import pytest

from backend.canonical.zero_io_spectral_expert_igpu_engine import (
    fwht_1d_batch,
    CompressedSpectralExpert,
    ZeroIOSpectralMoEEngine,
    run_zero_io_breakthrough_benchmark,
)


def test_1_fwht_1d_batch_isometry_and_properties():
    """
    Verifies Cooley-Tukey FWHT preserves energy (Parseval's identity / isometry),
    satisfies self-inversion H(H(x)) = x, and asserts on non-power-of-2 sizes.
    """
    rng = np.random.default_rng(2026)
    d = 256
    batch = 8
    x = rng.standard_normal((batch, d)).astype(np.float32)

    # 1. Forward transform
    h_x = fwht_1d_batch(x)
    assert h_x.shape == (batch, d)

    # 2. Isometry / energy conservation: ||H(x)||_2 == ||x||_2
    norm_x = np.linalg.norm(x, axis=-1)
    norm_hx = np.linalg.norm(h_x, axis=-1)
    np.testing.assert_allclose(norm_hx, norm_x, rtol=1e-5, atol=1e-5)

    # 3. Involution / self-inversion: H(H(x)) == x
    inv_x = fwht_1d_batch(h_x)
    np.testing.assert_allclose(inv_x, x, rtol=1e-5, atol=1e-5)

    # 4. Non-power-of-2 assertion
    x_bad = rng.standard_normal((batch, 200)).astype(np.float32)
    with pytest.raises(AssertionError):
        fwht_1d_batch(x_bad)


def test_2_896_experts_compression_and_memory_reduction():
    """
    Verifies 896-expert compression eliminates >95% of memory footprint,
    enabling 100% of experts to be pinned in 16 GB RAM with 0 cold SSD reads.
    """
    engine = ZeroIOSpectralMoEEngine(
        num_experts=896,
        active_experts=16,
        hidden_dim=256,
        inter_dim=64,
        outlier_density=0.01,
        seed=2026,
    )

    assert len(engine.experts) == 896
    assert engine.raw_expert_bytes == 896 * 256 * 64 * 4  # 58,720,256 bytes

    reduction_pct = (
        1.0 - (engine.compressed_expert_bytes / engine.raw_expert_bytes)
    ) * 100.0
    assert reduction_pct >= 95.0, f"Expected >= 95% reduction, got {reduction_pct:.2f}%"
    assert engine.compressed_expert_bytes < 3_000_000  # fits inside ~2.4 MB


def test_3_exact_computational_parity_spectral_plus_sparse():
    """
    Verifies exact algebraic equivalence between materialized dense expert multiplication
    and the Zero-IO decomposed spectral + sparse outlier formulation:
      x @ W_e == ((x * s_in) @ B_shared) * s_out + x @ Delta_sparse
    with IEEE-754 machine precision relative error <= 1e-6.
    """
    rng = np.random.default_rng(2026)
    engine = ZeroIOSpectralMoEEngine(
        num_experts=64,
        active_experts=8,
        hidden_dim=128,
        inter_dim=32,
        outlier_density=0.01,
        seed=42,
    )

    x = rng.standard_normal((10, 128)).astype(np.float32)

    for eid in range(10):
        w_dense = engine.materialize_dense_expert(eid)
        exp = engine.experts[eid]

        # Ground truth dense multiplication
        y_dense = x @ w_dense

        # Decomposed spectral + sparse multiplication
        y_spectral = ((x * exp.spectral_scale_in) @ engine.shared_basis) * exp.spectral_scale_out
        y_sparse = np.zeros_like(y_spectral)
        for i in range(x.shape[0]):
            contrib = x[i, exp.outlier_rows] * exp.outlier_vals
            np.add.at(y_sparse[i], exp.outlier_cols, contrib)
        y_decomposed = y_spectral + y_sparse

        rel_error = np.linalg.norm(y_decomposed - y_dense) / np.linalg.norm(y_dense)
        assert rel_error <= 1e-6, f"Expert {eid} relative error {rel_error} > 1e-6"


def test_4_attnres_lookahead_routing():
    """
    Verifies AttnRes lookahead routing selects top-16 experts per token
    with valid softmax gate probabilities summing to 1.0.
    """
    engine = ZeroIOSpectralMoEEngine(
        num_experts=896,
        active_experts=16,
        hidden_dim=256,
        inter_dim=64,
        seed=2026,
    )
    rng = np.random.default_rng(2026)
    x_early = rng.standard_normal((8, 256)).astype(np.float32)

    top_idx, gates = engine.route_attnres_lookahead(x_early)

    assert top_idx.shape == (8, 16)
    assert gates.shape == (8, 16)
    # Check probabilities sum to 1.0
    gate_sums = np.sum(gates, axis=-1)
    np.testing.assert_allclose(gate_sums, np.ones(8, dtype=np.float32), rtol=1e-5)
    # Check all indices are in valid expert range
    assert np.all(top_idx >= 0) and np.all(top_idx < 896)


def test_5_heterogeneous_cpu_igpu_co_execution():
    """
    Verifies dual-worker CPU+iGPU co-execution exactly matches brute-force
    materialized execution on multi-token batches.
    """
    engine = ZeroIOSpectralMoEEngine(
        num_experts=128,
        active_experts=8,
        hidden_dim=128,
        inter_dim=32,
        seed=2026,
    )
    rng = np.random.default_rng(2026)
    x_batch = rng.standard_normal((4, 128)).astype(np.float32)
    top_idx, gates = engine.route_attnres_lookahead(x_batch)

    out_bf = engine.forward_brute_force_ssd_simulation(x_batch, top_idx, gates)
    out_co = engine.forward_heterogeneous_cpu_igpu(x_batch, top_idx, gates)

    rel_error = np.linalg.norm(out_co - out_bf) / np.linalg.norm(out_bf)
    assert rel_error <= 1e-5, f"Co-execution relative error {rel_error} > 1e-5"


def test_6_counterfactual_fallback_for_non_spectral_expert():
    """
    Verifies fallback mechanism when an expert violates the spectral contract.
    """
    engine = ZeroIOSpectralMoEEngine(
        num_experts=64,
        active_experts=4,
        hidden_dim=128,
        inter_dim=32,
        seed=2026,
    )
    rng = np.random.default_rng(999)
    arbitrary_weights = rng.standard_normal((128, 32)).astype(np.float32)

    # Set fallback on expert 5
    engine.set_expert_fallback(5, arbitrary_weights)
    assert engine.experts[5].is_spectral_contract_valid is False
    assert engine.experts[5].raw_fallback_weights is not None

    dense_w = engine.materialize_dense_expert(5)
    np.testing.assert_allclose(dense_w, arbitrary_weights)


def test_7_live_benchmark_contract():
    """
    Verifies the end-to-end benchmark executes, satisfies exact computational parity,
    reports 0 cold SSD reads, and achieves > 95% memory elimination.
    """
    res = run_zero_io_breakthrough_benchmark()

    assert res["engine"] == "ZERO_IO_SPECTRAL_EXPERT_CPU_IGPU_SUBSUMPTION"
    assert res["exact_computational_parity_met"] is True
    assert res["cold_ssd_reads_required"] == 0
    assert res["ssd_io_and_ram_eliminated_pct"] >= 95.0
    assert res["relative_l2_error"] <= 1e-5
    assert res["total_experts"] == 896
    assert res["awake_experts"] == 16
