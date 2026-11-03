"""
tests/test_unseeded_terabyte_stream_subsumption.py
==================================================
Test suite for Project LEO: 100% Complete Replacement of Unseeded Terabyte Bitstreams
via Turnstile Ephemeral Ring-Buffer Sufficient Statistics and Clarkson-Woodruff CountSketch.

Target Hardware:
  Intel Core i5-12450H (AVX2/FMA/POPCNT) + 48-EU Intel UHD iGPU + 16 GB RAM + 512 GB NVMe SSD.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.canonical.unseeded_terabyte_stream_subsumption import (
    TurnstileEphemeralResult,
    turnstile_ephemeral_unseeded_stream,
    benchmark_turnstile_ephemeral_unseeded_stream,
    CountSketchStreamResult,
    clarkson_woodruff_countsketch_stream,
    benchmark_clarkson_woodruff_countsketch_stream,
    run_all_unseeded_terabyte_stream_subsumptions,
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


def test_1_turnstile_ephemeral_stream_exact_parity():
    """
    Asserts Turnstile Ephemeral Ring-Buffer matches monolithic X^T X and solve
    within <= 1e-6 relative error while achieving >= 12x memory reduction on
    holdout and > 1e7x at virtual 20.7 TB scale with ~1.32 MB peak L3 footprint.
    """
    res = benchmark_turnstile_ephemeral_unseeded_stream(
        holdout_t=4096, d=512, block_size=128, virtual_tb=20.7, seed=42
    )
    assert res.status == "PASS"
    assert res.is_mock is False
    assert res.gram_relative_error <= 1e-6
    assert res.weights_relative_error <= 1e-6
    assert res.holdout_memory_reduction_mult >= 12.0
    assert res.virtual_memory_reduction_mult > 1e7
    assert res.peak_ring_buffer_bytes <= 1_500_000


def test_2_clarkson_woodruff_countsketch():
    """
    Asserts Clarkson-Woodruff Block-Rademacher CountSketch stream achieves
    <= 0.01 unbiased trace energy relative error, exact row_compression_factor == 8.0,
    and > 1.2x end-to-end wall-clock speedup at d=512.
    """
    res = benchmark_clarkson_woodruff_countsketch_stream(
        T=8192, d=512, row_compression_factor=8.0, seed=42
    )
    assert res.status == "PASS"
    assert res.is_mock is False
    assert res.unbiased_trace_energy_rel_error <= 0.01
    assert abs(res.row_compression_factor - 8.0) < 1e-3
    assert res.speed_mult > 1.2
    assert res.sketch_buckets_s == 1024


def test_3_welford_running_variance_exactness():
    """
    Verifies Chan-Welford running mean and variance match exact NumPy statistics
    on an unseeded streaming white noise workload.
    """
    rng = np.random.default_rng(123)
    T, d = 2048, 256
    block_size = 128
    X = rng.standard_normal((T, d)).astype(np.float32)

    def block_gen():
        for i in range(0, T, block_size):
            yield X[i : i + block_size], None

    G, _, stats, _ = turnstile_ephemeral_unseeded_stream(
        block_gen(), d=d, ridge_lambda=1e-3, track_welford=True
    )

    gram_rel_err = float(np.linalg.norm(G - X.T @ X) / np.linalg.norm(X.T @ X))
    assert gram_rel_err <= 1e-6
    np.testing.assert_allclose(stats["running_mean"], np.mean(X, axis=0), rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(stats["running_var"], np.var(X, axis=0), rtol=1e-5, atol=1e-5)
    assert stats["total_rows_streamed"] == T


def test_4_adversarial_and_invalid_inputs():
    """
    Verifies robust validation and error-handling on adversarial/invalid inputs.
    """
    # Negative / zero dimension
    with pytest.raises(ValueError):
        turnstile_ephemeral_unseeded_stream([], d=0)

    # Incompatible stream block dimension
    with pytest.raises(ValueError):
        turnstile_ephemeral_unseeded_stream([(np.zeros((10, 5), dtype=np.float32), None)], d=6)

    # CountSketch 1D input
    with pytest.raises(ValueError):
        clarkson_woodruff_countsketch_stream(np.zeros(100, dtype=np.float32))

    # Invalid compression factor
    with pytest.raises(ValueError):
        clarkson_woodruff_countsketch_stream(np.zeros((100, 10), dtype=np.float32), row_compression_factor=0.5)


def test_5_functional_replacement_engine_dispatch():
    """
    Asserts FunctionalReplacementEngine dispatches both stream subsumptions cleanly.
    """
    engine = FunctionalReplacementEngine(seed=42)
    rng = np.random.default_rng(42)

    # 1. Ephemeral stream dispatch
    X_sample = rng.standard_normal((64, 32)).astype(np.float32)
    Y_sample = rng.standard_normal((64, 1)).astype(np.float32)
    G, W_star, stats, peak_bytes = engine.execute_turnstile_ephemeral_stream(
        [(X_sample, Y_sample)], d=32, k_targets=1
    )
    assert G.shape == (32, 32)
    assert W_star is not None
    assert W_star.shape == (32, 1)

    # 2. CountSketch dispatch
    X_dense = rng.standard_normal((128, 32)).astype(np.float32)
    sketch, G_sk, tr_e = engine.execute_clarkson_woodruff_countsketch(
        X_dense, row_compression_factor=4.0
    )
    assert sketch.shape == (32, 32)
    assert G_sk.shape == (32, 32)
    assert tr_e > 0.0


def test_6_composite_runner():
    """
    Asserts composite runner executes all benchmarks and returns verified passing results.
    """
    results = run_all_unseeded_terabyte_stream_subsumptions()
    assert "turnstile_ephemeral_stream" in results
    assert "clarkson_woodruff_countsketch" in results
    assert results["turnstile_ephemeral_stream"]["status"] == "PASS"
    assert results["clarkson_woodruff_countsketch"]["status"] == "PASS"
