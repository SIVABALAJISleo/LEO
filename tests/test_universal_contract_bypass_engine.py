"""
tests/test_universal_contract_bypass_engine.py
==============================================
Comprehensive integration tests for the Universal Contract & Pathway Bypass Engine.
Verifies the 5 core computational walls, algorithmic substitutions, and adversarial edge guards:
1. LogitSpaceHyperplaneAttention (Bypasses O(N^2) GPU Tensor Core Attention Wall)
2. ZerothOrderDualGradientSubsumer (Bypasses Backpropagation Activation VRAM Wall)
3. RemezMinimaxTranscendentalSubsumer (Bypasses GPU SFU Transcendental Wall)
4. HierarchicalRadianceCascadeSubsumer (Bypasses 4K Pixel Ray-Tracing Wall)
5. ZeroCopyHeterogeneousPipelineRouter (Bypasses PCIe Bus Host-to-Device Serialization Wall)
"""

import math
import numpy as np
import pytest
from scipy.special import erf

from backend.canonical.universal_contract_bypass_engine import (
    LogitSpaceHyperplaneAttention,
    ZerothOrderDualGradientSubsumer,
    RemezMinimaxTranscendentalSubsumer,
    HierarchicalRadianceCascadeSubsumer,
    ZeroCopyHeterogeneousPipelineRouter,
    run_universal_contract_bypass_suite,
)


def test_logit_space_hyperplane_attention():
    """Verify O(N^2) tensor core attention bypass via logit threshold projection."""
    audit = LogitSpaceHyperplaneAttention.run_audit(seq_len=256, head_dim=32, prune_tau=7.5)
    
    assert audit.contract_parity_met is True
    assert audit.measured_error < 0.05  # Relative L2 error < 5%
    assert audit.workload_reduction_ratio >= 2.0  # At least 2x fewer token-pair evaluations
    assert audit.adversarial_falsification_passed is True
    assert audit.raw_hardware_parity_claimed is False


def test_zeroth_order_dual_gradient_optimizer():
    """Verify VRAM backpropagation activation wall bypass via dual-gradient SPSA."""
    audit = ZerothOrderDualGradientSubsumer.run_audit(dim=16, n_samples=32, steps=100)
    
    assert audit.contract_parity_met is True
    assert audit.measured_error <= 0.10  # Training loss converged below 0.10
    assert audit.workload_reduction_ratio >= 10.0  # >90% memory savings
    assert audit.adversarial_falsification_passed is True
    assert audit.raw_hardware_parity_claimed is False


def test_remez_minimax_transcendental_subsumer():
    """Verify SFU transcendental bypass via degree-5 Abramowitz & Stegun rational kernel."""
    audit = RemezMinimaxTranscendentalSubsumer.run_audit(num_elements=100_000)
    
    assert audit.contract_parity_met is True
    assert audit.exact_parity_met is True
    assert audit.measured_error <= 1e-5  # Exact numerical parity
    assert audit.adversarial_falsification_passed is True
    assert audit.raw_hardware_parity_claimed is False

    # Detailed edge-case assertions
    x_test = np.array([-10.0, -2.0, 0.0, 2.0, 10.0], dtype=np.float32)
    ref = 0.5 * x_test * (1.0 + erf(x_test / math.sqrt(2.0)))
    approx = RemezMinimaxTranscendentalSubsumer.fast_gelu_minimax(x_test)
    np.testing.assert_allclose(approx, ref, atol=1e-5)

    # IEEE-754 edge traps
    x_ieee = np.array([np.nan, np.inf, -np.inf], dtype=np.float32)
    res_ieee = RemezMinimaxTranscendentalSubsumer.fast_gelu_minimax(x_ieee)
    assert np.isnan(res_ieee[0])
    assert np.isposinf(res_ieee[1])
    assert res_ieee[2] == 0.0


def test_hierarchical_radiance_cascade_subsumer():
    """Verify 4K per-pixel ray-tracing bypass via multi-scale radiance cascades."""
    audit = HierarchicalRadianceCascadeSubsumer.run_audit(res=64)
    
    assert audit.contract_parity_met is True
    assert audit.measured_error >= 25.0  # PSNR >= 25 dB
    assert audit.workload_reduction_ratio >= 3.0  # Ray budget cut by >= 3x
    assert audit.adversarial_falsification_passed is True
    assert audit.raw_hardware_parity_claimed is False


def test_zerocopy_heterogeneous_pipeline_router():
    """Verify PCIe serialization bypass via live Intel UHD OpenCL USM dispatch."""
    audit = ZeroCopyHeterogeneousPipelineRouter.run_audit(num_elements=131_072)
    
    assert audit.contract_parity_met is True
    assert audit.exact_parity_met is True
    assert audit.measured_error <= 1e-5
    assert audit.adversarial_falsification_passed is True
    assert audit.raw_hardware_parity_claimed is False


def test_master_universal_contract_bypass_suite():
    """Verify master suite orchestration and scientific honesty axioms."""
    report = run_universal_contract_bypass_suite()
    
    assert report["all_contracts_met"] is True
    assert report["all_adversarial_falsifications_passed"] is True
    assert report["raw_hardware_parity_claimed"] is False
    assert report["zero_simulated_timings"] is True
    assert report["external_dedicated_gpu_required"] is False
    assert len(report["audits"]) == 5
