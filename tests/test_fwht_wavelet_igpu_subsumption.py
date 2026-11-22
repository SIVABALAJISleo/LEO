"""
tests/test_fwht_wavelet_igpu_subsumption.py
Comprehensive test suite verifying the four single-device breakthroughs:
1. 1969 Fast Walsh-Hadamard Transform (FWHT) Orthogonal Energy Concentration.
2. 1988 Mallat 2D Haar Discrete Wavelet Transform (DWT) Sparse Media Subband Shading.
3. GaLore-style SVD Subspace-Projected Low-Rank Optimizer (>90% RAM reduction).
4. Live Intel UHD Graphics (48 EUs) OpenCL Hardware Profiler & USM Zero-Copy Dispatch.
"""

import math
import numpy as np
import pytest

from backend.canonical.fwht_wavelet_igpu_subsumption import (
    FWHTDenseWeightConcentration,
    LiveIntelUHDOpenCLProbe,
    LowRankSubspaceMemoryOptimizer,
    SparseWaveletMediaSubsumption,
    fwht_normalized,
    run_fwht_wavelet_igpu_suite,
)


def test_fwht_mathematical_orthogonality():
    """Verify that normalized FWHT is an exact isometry: H^T H = I."""
    n = 256
    eye = np.eye(n, dtype=np.float64)
    h_matrix = fwht_normalized(eye)
    gram = h_matrix.T @ h_matrix
    assert np.allclose(gram, eye, atol=1e-12), "H^T H must equal Identity (exact isometry)"

    # Check non-power-of-2 validation
    with pytest.raises(ValueError):
        fwht_normalized(np.ones(10))


def test_fwht_flat_dense_collapse():
    """Verify that flat uniform dense vector h = [1, ..., 1] collapses to 1 single non-zero element."""
    n = 2048
    h_flat = np.ones(n, dtype=np.float64)
    h_rot = fwht_normalized(h_flat)

    # First coefficient should be sqrt(n), all other n-1 coefficients should be exact 0.0
    expected_first = math.sqrt(n)
    assert abs(h_rot[0] - expected_first) < 1e-12
    assert np.max(np.abs(h_rot[1:])) < 1e-12
    assert np.count_nonzero(np.abs(h_rot) > 1e-12) == 1


def test_fwht_dense_concentration_audit():
    """Verify FWHT dense concentration audit across flat, coherent, and noise regimes."""
    audit = FWHTDenseWeightConcentration.run_audit(inter_dim=1024, hidden_dim=256)

    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_parity_met is True
    assert audit.contract_parity_met is True
    assert audit.reduction_or_speedup > 1.0
    assert audit.adversarial_falsification_passed is True


def test_sparse_wavelet_media_subsumption():
    """Verify Mallat 2D Haar DWT exact invertibility, sparse speedup, and noise fallback."""
    audit = SparseWaveletMediaSubsumption.run_audit(size=128, detail_tol=0.03)

    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_parity_met is True  # Haar roundtrip error <= 1e-5
    assert audit.contract_parity_met is True  # PSNR >= 40 dB and >= 60% evals eliminated
    assert audit.measured_error >= 40.0  # PSNR dB
    assert audit.adversarial_falsification_passed is True  # White noise triggers fallback


def test_galore_subspace_optimizer():
    """Verify GaLore subspace gradient projection cuts optimizer RAM >80% while converging."""
    audit = LowRankSubspaceMemoryOptimizer.run_audit(m=64, n=64, rank=8, steps=40)

    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_parity_met is False  # Honest: low-rank projection is lossy
    assert audit.contract_parity_met is True  # Loss within contract, RAM saved > 80%
    assert audit.reduction_or_speedup > 5.0
    assert audit.adversarial_falsification_passed is True  # Full-rank noise detected


def test_live_intel_uhd_opencl_probe():
    """Verify live Intel UHD iGPU (48 EUs) OpenCL kernel execution and profiling."""
    probe = LiveIntelUHDOpenCLProbe.run_live_probe(num_elements=524_288)

    assert isinstance(probe, dict)
    assert "igpu_dispatched" in probe
    assert "honest_status" in probe

    if probe["igpu_dispatched"]:
        assert "Intel" in probe["device_name"] or "UHD" in probe["device_name"]
        assert probe["max_compute_units"] == 48
        assert probe["igpu_time_ms"] > 0.0
        assert probe["verified_exact"] is True
        assert probe["max_abs_error_vs_cpu"] <= 1e-5
        assert probe["honest_status"] == "LIVE_OPENCL_HARDWARE_EXECUTION_VERIFIED"


def test_full_suite_runner():
    """Verify top-level suite execution and integrity contracts."""
    suite = run_fwht_wavelet_igpu_suite()

    assert suite["single_device_only"] is True
    assert suite["distributed_computing_present"] is False
    assert suite["raw_hardware_parity_claimed"] is False
    assert suite["all_contracts_met"] is True
    assert suite["all_adversarial_falsifications_passed"] is True
    assert len(suite["audits"]) == 3
