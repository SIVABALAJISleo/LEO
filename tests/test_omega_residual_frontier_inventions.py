"""
tests/test_omega_residual_frontier_inventions.py

Test Suite for Pure Single-Device Residual Frontier Inventions:
1. Pre-Read Cauchy-Schwarz Dense SwiGLU Row-Norm Skipper
2. Unrelated-User Micro-Batch Superposition & LSH
3. Keyframe-Only Optical-Flow Video Advection
4. 1977 Brandt Optimal O(N) Non-Periodic Multigrid FP64
"""

from backend.canonical.omega_residual_frontier_inventions import (
    PreReadCauchySchwarzDenseSkipper,
    UnrelatedUserSuperpositionServer,
    OpticalFlowKeyframeVideoSubsumption,
    OptimalONMultigridNonPeriodicFP64Solver,
    run_omega_residual_frontier_suite,
)


def test_1_cauchy_schwarz_swiglu_row_skipping():
    audit = PreReadCauchySchwarzDenseSkipper.run_audit(
        hidden_dim=512,
        inter_dim=2048,
        energy_capture_target=0.94,
    )
    assert audit.contract_parity_met is True
    assert audit.exact_or_certified_parity is True
    assert audit.reduction_or_speedup >= 2.0
    assert audit.measured_error <= 0.03
    assert audit.raw_hardware_parity_claimed is False
    assert audit.single_device_only is True


def test_2_cauchy_schwarz_flat_spectrum_adversarial_fallback():
    audit = PreReadCauchySchwarzDenseSkipper.run_audit()
    assert audit.adversarial_falsification_passed is True


def test_3_unrelated_user_microbatch_superposition():
    audit = UnrelatedUserSuperpositionServer.run_audit(
        num_users=32,
        hidden_dim=128,
        out_dim=128,
        lsh_bits=5,
    )
    assert audit.contract_parity_met is True
    assert audit.exact_or_certified_parity is True
    assert audit.reduction_or_speedup == 32.0
    assert audit.measured_error <= 1e-4
    assert audit.single_device_only is True


def test_4_unrelated_user_lsh_adversarial_spread():
    audit = UnrelatedUserSuperpositionServer.run_audit()
    assert audit.adversarial_falsification_passed is True


def test_5_optical_flow_video_advection():
    audit = OpticalFlowKeyframeVideoSubsumption.run_audit(
        num_frames=8,
        height=64,
        width=64,
        keyframe_stride=4,
    )
    assert audit.contract_parity_met is True
    assert audit.measured_error >= 28.0
    assert audit.reduction_or_speedup >= 2.0
    assert audit.single_device_only is True


def test_6_optical_flow_jump_cut_adversarial_fallback():
    audit = OpticalFlowKeyframeVideoSubsumption.run_audit()
    assert audit.adversarial_falsification_passed is True


def test_7_brandt_optimal_on_multigrid_nonperiodic_fp64():
    audit = OptimalONMultigridNonPeriodicFP64Solver.run_audit(
        grid_n=33,
        v_cycles=10,
        baseline_sweeps=200,
    )
    assert audit.contract_parity_met is True
    assert audit.exact_or_certified_parity is True
    assert audit.measured_error <= 1e-9
    assert audit.single_device_only is True


def test_8_brandt_multigrid_helmholtz_indefinite_fallback():
    audit = OptimalONMultigridNonPeriodicFP64Solver.run_audit()
    assert audit.adversarial_falsification_passed is True


def test_9_full_omega_residual_frontier_suite_execution():
    results = run_omega_residual_frontier_suite()
    assert results["engine"] == "LEO_PURE_SINGLE_DEVICE_OMEGA_RESIDUAL_INVENTIONS"
    assert results["distributed_computing_present"] is False
    assert results["raw_hardware_parity_claimed"] is False
    assert results["all_contracts_met"] is True
    assert results["all_adversarial_falsifications_passed"] is True
    assert len(results["audits"]) == 4
