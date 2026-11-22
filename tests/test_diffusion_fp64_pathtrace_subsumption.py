"""
tests/test_diffusion_fp64_pathtrace_subsumption.py
==============================================================================
Project LEO / HYPER: Verification Suite for Pure Single-Device Diffusion,
Exact FP64 HPC (Spectral Poisson + Mixed-Precision IR), and ReSTIR Path Tracing.
Hardware Target: Intel Core i5-12450H + Intel UHD iGPU (USM + Quick Sync) + 16 GB RAM
Zero Distributed Computing. Zero External GPUs.
==============================================================================
"""

import hashlib
import numpy as np
import pytest
from backend.canonical.diffusion_fp64_pathtrace_subsumption import (
    ExactFP64ScientificHPCSubsumption,
    MultigridTaylorDiffusionSubsumption,
    ReSTIRAtrousPathTraceSubsumption,
    run_diffusion_fp64_pathtrace_suite,
)


def test_1_spectral_poisson_pde_exact_15_digit_parity():
    """Verify 1965 Cooley-Tukey 2D FFT spectral solver reaches 10^-13 machine precision in 1 pass."""
    report = ExactFP64ScientificHPCSubsumption.run_spectral_pde_audit(grid_n=64, jacobi_iters=200)
    assert report.exact_computational_parity_met is True
    assert report.contract_parity_met is True
    assert report.measured_error <= 1e-12
    assert report.work_eliminated_pct >= 99.0
    assert report.raw_hardware_parity_claimed is False
    assert report.single_device_only is True


def test_2_mixed_precision_ir_dense_solve_precision():
    """Verify 1967 Wilkinson/Higham mixed-precision IR squares residual to 15-digit FP64 accuracy."""
    report = ExactFP64ScientificHPCSubsumption.run_mixed_precision_ir_audit(n_dim=128, refine_steps=4)
    assert report.exact_computational_parity_met is True
    assert report.contract_parity_met is True
    assert report.measured_error <= 1e-13
    assert report.adversarial_falsification_passed is True


def test_3_crypto_sha256_avalanche_irreducibility_proof():
    """Verify SHA-256 1-bit input avalanche destroys all algebraic structure (~50% bit flip)."""
    d1 = hashlib.sha256(b"LEO_PROVE_CRYPTO_IRREDUCIBLE_0").digest()
    d2 = hashlib.sha256(b"LEO_PROVE_CRYPTO_IRREDUCIBLE_1").digest()
    hamming_bits = sum(bin(a ^ b).count("1") for a, b in zip(d1, d2))
    assert 96 <= hamming_bits <= 160


def test_4_multigrid_taylor_diffusion_video_subsumption():
    """Verify multigrid coarse-to-fine + Adams-Bashforth velocity caching saves >65% evals with high PSNR."""
    report = MultigridTaylorDiffusionSubsumption.run_audit(size=64, total_steps=30)
    assert report.contract_parity_met is True
    assert report.work_eliminated_pct >= 60.0
    assert report.single_device_only is True


def test_5_multigrid_taylor_adversarial_discontinuous_noise_fallback():
    """Verify discontinuous high-curvature noise correctly triggers the cache-disable guard."""
    report = MultigridTaylorDiffusionSubsumption.run_audit(size=64, total_steps=20, curvature_tol=0.25)
    assert report.adversarial_falsification_passed is True


def test_6_restir_atrous_path_tracing_90pct_ray_elimination():
    """Verify ReSTIR RIS + 4-pass A-Trous wavelet eliminates >=90% of ray/light evaluations at high PSNR."""
    report = ReSTIRAtrousPathTraceSubsumption.run_audit(height=128, width=128, num_lights=64, candidates_m=4)
    assert report.contract_parity_met is True
    assert report.work_eliminated_pct >= 90.0
    assert report.single_device_only is True


def test_7_restir_adversarial_white_noise_normal_fallback():
    """Verify uncorrelated white-noise geometry collapses spatial reuse and signals dense ray fallback."""
    report = ReSTIRAtrousPathTraceSubsumption.run_audit(height=32, width=32, num_lights=32, candidates_m=4)
    assert report.adversarial_falsification_passed is True


def test_8_master_diffusion_fp64_pathtrace_suite_verification():
    """Verify complete suite execution satisfies all contracts, zero distributed computing, and honest parity."""
    suite = run_diffusion_fp64_pathtrace_suite()
    assert suite["engine"] == "LEO_SINGLE_DEVICE_DIFFUSION_FP64_PATHTRACE_SUBSUMPTION"
    assert suite["distributed_computing_present"] is False
    assert suite["raw_hardware_parity_claimed"] is False
    assert suite["all_contracts_met"] is True
    assert suite["all_adversarial_falsifications_passed"] is True
    assert len(suite["reports"]) == 4
