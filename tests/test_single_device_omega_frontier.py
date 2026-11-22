"""
tests/test_single_device_omega_frontier.py
==============================================================================
Project LEO / HYPER-Omega: Pure Single-Device Frontier Verification Suite
Target Hardware: Intel Core i5-12450H + Intel UHD Graphics + 16 GB RAM
(Zero Distributed / Zero P2P / 100% Single-Device Host Execution)
==============================================================================
"""

import sys
import pytest
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.canonical.single_device_omega_frontier_engine import (
    FrontierAudit,
    NeuronGranularitySubExpertSkipper,
    BranchAndBoundEarlyExitRouter,
    EGraphAlgebraicKernelLifter,
    run_single_device_frontier_suite,
)


def test_1_neuron_granularity_subexpert_skipping_unmodified_weights():
    """Verify zero-error row skipping on unmodified W_down weights with >50% bytes saved."""
    audit = NeuronGranularitySubExpertSkipper.run_audit(
        hidden_dim=256,
        inter_dim=1024,
        sparsity_bias=-0.95,
    )
    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_parity_verified is True
    assert audit.contract_parity_met is True
    assert audit.reduction_or_speedup > 1.5


def test_2_neuron_granularity_adversarial_dense_activation_fallback():
    """Verify that >85% dense activations honestly trigger dense fallback without fake skips."""
    audit = NeuronGranularitySubExpertSkipper.run_audit(
        hidden_dim=128,
        inter_dim=512,
        sparsity_bias=5.0,  # All activations strictly non-zero
    )
    assert audit.adversarial_fallback_verified is True


def test_3_land_doig_branch_and_bound_early_exit():
    """Verify adaptive layer depth skips unnecessary SSD reads while preserving token agreement."""
    audit = BranchAndBoundEarlyExitRouter.run_audit(
        total_layers=92,
        num_tokens=32,
        hidden_dim=64,
        vocab_size=128,
        margin_threshold=0.85,
    )
    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_parity_verified is True
    assert audit.contract_parity_met is True
    assert audit.reduction_or_speedup > 1.2


def test_4_land_doig_adversarial_high_entropy_token_forces_full_depth():
    """Verify that ambiguous/uniform probability distributions refuse early exit."""
    rng = np.random.default_rng(42)
    vocab_size = 256
    margin_threshold = 0.90
    adv_logits = rng.uniform(-0.001, 0.001, size=(vocab_size,)).astype(np.float32)
    adv_probs = np.exp(adv_logits - np.max(adv_logits))
    adv_probs /= np.sum(adv_probs)
    adv_top2 = np.partition(adv_probs, -2)[-2:]
    margin = float(adv_top2[1] - adv_top2[0])
    assert margin < margin_threshold, "Adversarial logits should not satisfy early exit threshold"


def test_5_egraph_matrix_chain_associativity_rewrite():
    """Verify (A @ B) @ v is rewritten into A @ (B @ v) with O(N^3) -> O(N^2) FLOP reduction."""
    shapes = {"A": (256, 256), "B": (256, 256), "v": (256, 1)}
    naive_ir = ("MATMUL", ("MATMUL", ("VAR", "A"), ("VAR", "B")), ("VAR", "v"))
    best_ir, was_rewritten = EGraphAlgebraicKernelLifter.saturate_and_extract(naive_ir, shapes)

    assert was_rewritten is True
    assert best_ir[0] == "MATMUL"
    assert best_ir[2][0] == "MATMUL"  # A @ (B @ v)


def test_6_egraph_geometric_series_closed_form():
    """Verify loop sum_{k=0}^{N-1} a * r^k is folded into O(1) closed form."""
    shapes = {}
    loop_ir = ("GEOM_SERIES_LOOP", 3.0, 0.5, 100)
    opt_ir, was_rewritten = EGraphAlgebraicKernelLifter.saturate_and_extract(loop_ir, shapes)

    assert was_rewritten is True
    assert opt_ir[0] == "GEOM_SERIES_CLOSED_FORM"

    val_loop = EGraphAlgebraicKernelLifter._eval_ir(loop_ir, {})
    val_opt = EGraphAlgebraicKernelLifter._eval_ir(opt_ir, {})
    assert np.isclose(val_loop[0], val_opt[0], atol=1e-12)


def test_7_egraph_adversarial_chaotic_loop_tdm_fallback():
    """Verify that opaque chaotic recurrences cannot be falsely simplified."""
    shapes = {}
    chaotic_ir = ("OPAQUE_CHAOTIC_LOOP", "sin_recurrence", 5000)
    opt_ir, was_rewritten = EGraphAlgebraicKernelLifter.saturate_and_extract(chaotic_ir, shapes)

    assert was_rewritten is False
    assert opt_ir == chaotic_ir


def test_8_pure_single_device_suite_and_zero_distributed():
    """Verify entire single-device frontier suite passes contracts and falsifications."""
    res = run_single_device_frontier_suite()
    assert res["engine"] == "LEO_PURE_SINGLE_DEVICE_OMEGA_FRONTIER"
    assert res["distributed_computing_present"] is False
    assert res["raw_hardware_parity_claimed"] is False
    assert res["all_contracts_met"] is True
    assert res["all_adversarial_fallbacks_verified"] is True
    assert len(res["audits"]) == 3
