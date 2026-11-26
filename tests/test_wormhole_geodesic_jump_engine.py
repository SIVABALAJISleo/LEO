"""
tests/test_wormhole_geodesic_jump_engine.py
============================================
Verification suite for LEO / HYPER-Omega Computational Wormhole
and Trajectory-Jump Geodesic Engine.

Verifies:
1. Logarithmic Time-Wormhole (Binary Affine Operator Squaring)
2. Mean-Flow Shortcut Trajectory-Jump Wormhole
3. HyPINO Residual-Stabilized Superposition Portal
4. Complete Geodesic Suite Runner and Adversarial Invariants
"""

from backend.canonical.wormhole_geodesic_jump_engine import (
    LogarithmicTimeWormhole,
    MeanFlowShortcutWormhole,
    ResidualStabilizedWormhole,
    run_wormhole_geodesic_suite,
)


def test_logarithmic_time_wormhole_execution_and_adversarial():
    audit = LogarithmicTimeWormhole.run_audit(dim=32, total_steps_t=1024)
    assert audit.portal_name == "Logarithmic_Operator_Squaring_Time_Wormhole"
    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_or_certified_parity is True
    assert audit.contract_parity_met is True
    assert audit.wormhole_length_L <= 10
    assert audit.long_path_distance_D == 1024
    assert audit.path_collapse_ratio >= 100.0
    assert audit.measured_error <= 1e-11
    assert audit.adversarial_falsification_passed is True


def test_mean_flow_shortcut_wormhole_execution_and_adversarial():
    audit = MeanFlowShortcutWormhole.run_audit(
        dim=64, fine_steps=32, macro_jumps=2, consistency_tol=0.05
    )
    assert audit.portal_name == "MeanFlow_Shortcut_Trajectory_Jump_Wormhole"
    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_or_certified_parity is True
    assert audit.contract_parity_met is True
    assert audit.wormhole_length_L == 6
    assert audit.long_path_distance_D == 128
    assert audit.measured_error <= 1e-3
    assert audit.adversarial_falsification_passed is True


def test_residual_stabilized_wormhole_execution_and_adversarial():
    audit = ResidualStabilizedWormhole.run_audit(
        dim=128, max_refinements=15, target_tol=1e-12
    )
    assert audit.portal_name == "HyPINO_Residual_Stabilized_Superposition_Portal"
    assert audit.single_device_only is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_or_certified_parity is True
    assert audit.contract_parity_met is True
    assert audit.measured_error <= 1e-11
    assert audit.adversarial_falsification_passed is True


def test_full_wormhole_geodesic_suite_closure():
    suite_res = run_wormhole_geodesic_suite()
    assert suite_res["engine"] == "LEO_COMPUTATIONAL_WORMHOLE_GEODESIC_SUITE"
    assert suite_res["single_device_only"] is True
    assert suite_res["distributed_computing_present"] is False
    assert suite_res["raw_hardware_parity_claimed"] is False
    assert suite_res["all_portals_verified"] is True
    assert suite_res["all_adversarial_guards_passed"] is True
    assert len(suite_res["audits"]) == 3
