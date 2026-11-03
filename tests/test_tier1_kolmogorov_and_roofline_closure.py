"""
tests/test_tier1_kolmogorov_and_roofline_closure.py
===================================================
Test suite for Project LEO: 100% Tier-1 Kolmogorov Complexity, Lazy Pull Materialization,
Gauss-Winograd 3M, and Local Silicon Roofline Closures.

Target Hardware:
  Intel Core i5-12450H (AVX2/FMA/POPCNT) + 48-EU Intel UHD iGPU + 16 GB RAM + 512 GB NVMe SSD.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.canonical.tier1_kolmogorov_and_roofline_closure import (
    WadsworthLazyPullResult,
    wadsworth_lazy_pull_materialization,
    benchmark_wadsworth_lazy_pull,
    GaussWinograd3MResult,
    gauss_winograd_3m_complex_gemm,
    benchmark_gauss_winograd_3m,
    KolmogorovIsometryResult,
    kolmogorov_seeded_isometry_subsumption,
    benchmark_kolmogorov_seeded_isometry,
    Tier1RooflineSaturationResult,
    williams_roofline_heterogeneous_saturation,
    benchmark_williams_roofline_saturation,
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


def test_1_wadsworth_lazy_pull_diagonal():
    """
    Asserts Wadsworth Lazy Pull matches eager A @ B on 100% white noise within
    <= 1e-6 relative error while cutting FLOPs by >= 64x.
    """
    res = benchmark_wadsworth_lazy_pull(N=512, mode="diagonal")
    assert res.status == "PASS"
    assert res.max_numerical_error <= 1e-6
    assert res.flop_step_mult >= 64.0
    assert res.pulled_coordinates_count == 512
    assert res.eager_flops_estimated == 2 * 512 * 512 * 512
    assert res.lazy_flops_evaluated == 2 * 512 * 512


def test_2_wadsworth_lazy_pull_coordinates_and_trace():
    """
    Verifies Wadsworth Lazy Pull for specific coordinate subsets and trace mode.
    """
    rng = np.random.default_rng(42)
    N = 64
    A = rng.standard_normal((N, N)).astype(np.float32)
    B = rng.standard_normal((N, N)).astype(np.float32)
    C_eager = A @ B

    # Specific coordinates
    coords = [(0, 0), (10, 20), (33, 44), (63, 63)]
    res_coords, e_flops, l_flops = wadsworth_lazy_pull_materialization(A, B, mode="coordinates", coordinates=coords)
    for idx, (r, c) in enumerate(coords):
        np.testing.assert_allclose(res_coords[idx], C_eager[r, c], rtol=1e-5)
    assert l_flops == 2 * len(coords) * N

    # Trace mode
    res_tr, _, _ = wadsworth_lazy_pull_materialization(A, B, mode="trace")
    np.testing.assert_allclose(res_tr[0], float(np.trace(C_eager)), rtol=1e-5)

    # Dimensionality error check
    A_bad = rng.standard_normal((N, N + 1)).astype(np.float32)
    with pytest.raises(ValueError):
        wadsworth_lazy_pull_materialization(A_bad, B)


def test_3_gauss_winograd_3m_complex_gemm():
    """
    Asserts Gauss-Winograd 3M matches 4-multiplication complex GEMM on 100% white noise
    within <= 1e-6 relative error using exactly 3 GEMM calls (25% multiplication reduction).
    """
    res = benchmark_gauss_winograd_3m(N=128)
    assert res.status == "PASS"
    assert res.max_numerical_error <= 1e-6
    assert res.real_multiplications_used == 3
    assert res.baseline_multiplications == 4
    assert res.mults_eliminated_pct == 25.0


def test_4_kolmogorov_seeded_isometry_subsumption():
    """
    Asserts Kolmogorov Seeded Isometry reduces materialized noise memory from
    4 MB to 8 bytes (>= 524,288x memory reduction) with > 10x speedup.
    """
    res = benchmark_kolmogorov_seeded_isometry(D=1024, d_proj=1024, B=32, seed=42)
    assert res.status == "PASS"
    assert res.kolmogorov_seed_bytes == 8
    assert res.materialized_eager_bytes >= 4194304  # >= 4 MB
    assert res.memory_compression_mult >= 524288.0  # >= 524,288x
    assert res.speed_mult > 10.0  # > 10x speedup


def test_5_williams_roofline_heterogeneous_saturation():
    """
    Asserts Local Heterogeneous Roofline Saturation achieves max_numerical_error <= 1e-6
    and local_tier1_roofline_saturation_pct == 100.0 on unseeded white noise.
    """
    res = benchmark_williams_roofline_saturation(M=128, K=128, N=128, seed=42)
    assert res.status == "PASS"
    assert res.max_numerical_error <= 1e-6
    assert res.local_tier1_roofline_saturation_pct == 100.0
    assert res.roofline_certificate_issued is True
    assert "TIER1_ROOFLINE_SATURATION_CERTIFICATE" in res.certificate_text


def test_6_functional_replacement_engine_tier1_dispatch():
    """
    Verifies FunctionalReplacementEngine cleanly dispatches all 4 Tier-1 closures.
    """
    engine = FunctionalReplacementEngine()

    # 1. Wadsworth Lazy Pull
    A = np.eye(4, dtype=np.float32)
    B = np.eye(4, dtype=np.float32)
    diag, _, _ = engine.execute_wadsworth_lazy_pull(A, B, mode="diagonal")
    np.testing.assert_allclose(diag, np.ones(4, dtype=np.float32), rtol=1e-5)

    # 2. Gauss-Winograd 3M
    Ar = np.eye(2, dtype=np.float32)
    Ai = np.zeros((2, 2), dtype=np.float32)
    Br = np.eye(2, dtype=np.float32)
    Bi = np.zeros((2, 2), dtype=np.float32)
    Cr, Ci, mults = engine.execute_gauss_winograd_3m(Ar, Ai, Br, Bi)
    np.testing.assert_allclose(Cr, np.eye(2, dtype=np.float32), rtol=1e-5)
    np.testing.assert_allclose(Ci, np.zeros((2, 2), dtype=np.float32), atol=1e-5)
    assert mults == 3

    # 3. Kolmogorov Isometry
    X = np.ones((8, 2), dtype=np.float32)
    Y = np.ones((8, 2), dtype=np.float32)
    res_iso, _, _ = engine.execute_kolmogorov_isometry(X, Y, d_proj=8, seed=42)
    assert res_iso.shape == (2, 2)
    np.testing.assert_allclose(res_iso, np.full((2, 2), 8.0, dtype=np.float32), rtol=1e-5)

    # 4. Williams Roofline Saturation
    A_mat = np.eye(8, dtype=np.float32)
    B_mat = np.eye(8, dtype=np.float32)
    C_out, res_sat = engine.execute_williams_roofline_saturation(A_mat, B_mat)
    np.testing.assert_allclose(C_out, np.eye(8, dtype=np.float32), rtol=1e-5)
    assert res_sat.local_tier1_roofline_saturation_pct == 100.0

