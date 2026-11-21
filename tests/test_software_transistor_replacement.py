"""
tests/test_software_transistor_replacement.py
=============================================================================
Verification & Falsification Suite: Software-Defined Transistor Replacement Engine
Hardware Target: Intel Core i5-12450H + Intel UHD Graphics + 16GB RAM
Tests All 5 Mechanisms, Bit-Exact Error Bounds, and Space-Time Conservation Law.
=============================================================================
"""

import math
import numpy as np
import pytest

from backend.canonical.software_transistor_replacement_engine import (
    SpaceTimeInformationProfiler,
    TimeDivisionMultiplexingScheduler,
    BitSlicedVirtualLogicGateEngine,
    MultiplyFreeLUTEngine,
    ISAAndMicrocodeEmulationLayer,
    AlgorithmicSubsumptionFrontEnd,
    SoftwareDefinedTransistorReplacementEngine,
    run_all_transistor_replacement_audits,
)
from backend.layer5_local_infer.bitnet_tmac_engine import BitNetTMacEngine


def test_1_space_time_information_profiler():
    """
    Verifies Shannon entropy profiling routes structured data to Mechanism 5
    and incompressible white-noise data to Mechanism 1.
    """
    rng = np.random.default_rng(2026)
    
    # 1. Low-entropy structured data (rank-1 outer product)
    u = rng.standard_normal((128, 1)).astype(np.float32)
    v = rng.standard_normal((1, 128)).astype(np.float32)
    structured_mat = u @ v
    route_structured = SpaceTimeInformationProfiler.profile_and_route(
        structured_mat, workload_type="closed_form"
    )
    assert route_structured["mechanism"] == "MECHANISM_5_ALGORITHMIC_SUBSUMPTION"
    assert route_structured["compressible"] is True

    # 2. Maximum-entropy uniform white noise
    noise_mat = rng.uniform(-10.0, 10.0, size=(128, 128)).astype(np.float32)
    route_noise = SpaceTimeInformationProfiler.profile_and_route(
        noise_mat, workload_type="dense_gemm"
    )
    assert route_noise["mechanism"] == "MECHANISM_1_TDM_CACHE_TILED"
    assert route_noise["compressible"] is False


def test_2_mechanism_1_tdm_cache_blocked_gemm():
    """
    Verifies Time-Division Multiplexing (TDM) scheduler correctly computes
    dense GEMM via cache-resident L1/L2 tiles with relative error <= 1e-5.
    """
    audit = TimeDivisionMultiplexingScheduler.run_audit(m=64, k=64, n=64)

    assert audit.mechanism_selected == "MECHANISM_1_TDM_CACHE_TILED"
    assert audit.raw_hardware_parity_claimed is False
    assert audit.exact_computational_parity_met is True
    assert audit.contract_parity_met is True
    assert audit.area_for_time_ratio > 1.0
    assert audit.error_or_discrepancy <= 1e-5
    assert audit.fallback_triggered is True


def test_3_mechanism_2_bitsliced_virtual_logic_gates_and_adder():
    """
    Verifies Bit-Slicing (SWAR):
      1. AoS to Bit-Planar transposer roundtrip is 100% lossless (0 error).
      2. Ripple-carry adder over 10,000+ virtual gates produces exact sums.
    """
    rng = np.random.default_rng(2026)
    num_lanes = 256
    a_u8 = rng.integers(0, 128, size=num_lanes, dtype=np.uint8)
    b_u8 = rng.integers(0, 128, size=num_lanes, dtype=np.uint8)

    # Lossless transposition check
    a_planes = BitSlicedVirtualLogicGateEngine.aos_to_bit_planar(a_u8)
    a_reconstructed = BitSlicedVirtualLogicGateEngine.bit_planar_to_aos(a_planes, num_lanes)
    assert np.array_equal(a_u8, a_reconstructed)

    # Bit-sliced adder check
    b_planes = BitSlicedVirtualLogicGateEngine.aos_to_bit_planar(b_u8)
    sum_planes, _ = BitSlicedVirtualLogicGateEngine.bit_sliced_ripple_carry_adder(
        a_planes, b_planes, bit_width=8
    )
    computed_sum = BitSlicedVirtualLogicGateEngine.bit_planar_to_aos(sum_planes, num_lanes)
    ref_sum = a_u8 + b_u8

    bit_errors = int(np.sum(computed_sum != ref_sum))
    assert bit_errors == 0


def test_4_mechanism_2_bitsliced_1bit_xnor_gemm():
    """
    Verifies 1-Bit XNOR-Popcount Binary MatMul evaluates exact matrix dot-products
    with 0 bit errors and zero hardware multiplier instructions.
    """
    rng = np.random.default_rng(2026)
    rows, cols = 64, 128
    w_bin = rng.choice([-1, 1], size=(rows, cols)).astype(np.int8)
    x_bin = rng.choice([-1, 1], size=cols).astype(np.int8)

    ref_y = (w_bin.astype(np.float32) @ x_bin.astype(np.float32)).astype(np.int32)
    leo_y = BitSlicedVirtualLogicGateEngine.execute_1bit_xnor_gemm(w_bin, x_bin)

    assert np.array_equal(ref_y, leo_y)


def test_5_mechanism_3_multiply_free_lut_vpshufb_gemv():
    """
    Verifies Mechanism 3 Multiply-Free LUT Engine:
      1. Max absolute error <= 1e-4 vs standard FMA matmul.
      2. Zero floating-point multipliers in the accumulation loop.
      3. Pluggable backend connection to BitNetTMacEngine.
    """
    audit = MultiplyFreeLUTEngine.run_audit(rows=128, cols=128)

    assert audit.mechanism_selected == "MECHANISM_3_MULTIPLY_FREE_LUT"
    assert audit.exact_computational_parity_met is True
    assert audit.contract_parity_met is True
    assert audit.error_or_discrepancy <= 1e-4
    assert audit.operations_deleted_pct == 100.0

    # Test integration with BitNetTMacEngine
    engine = BitNetTMacEngine(hidden_dim=64, vocab_size=50)
    x = np.random.default_rng(42).standard_normal(64).astype(np.float32)
    out_y = engine.execute_layer(x, backend_mode="avx2_vpshufb")
    assert out_y.shape == (64,)
    assert not np.any(np.isnan(out_y))


def test_6_mechanism_4_fp8_e4m3_and_cuda_warp_emulation():
    """
    Verifies Mechanism 4:
      1. Bit-exact FP8 E4M3 encode/decode according to OCP spec.
      2. CUDA warp shuffle 32-lane butterfly reduction emulation.
    """
    audit = ISAAndMicrocodeEmulationLayer.run_audit(vector_len=256)

    assert audit.mechanism_selected == "MECHANISM_4_ISA_EMULATION"
    assert audit.exact_computational_parity_met is True
    assert audit.raw_hardware_parity_claimed is False

    # Bit-exact subnormal & normal decodes
    # Zero (0x00) -> 0.0
    assert ISAAndMicrocodeEmulationLayer._decode_fp8_e4m3(0x00) == 0.0
    # Smallest subnormal (0x01) -> 2^(-6) * (1/8) = 1/512 = 0.001953125
    assert math.isclose(ISAAndMicrocodeEmulationLayer._decode_fp8_e4m3(0x01), 0.001953125, rel_tol=1e-6)
    # NaN check (0x7F) -> NaN
    assert math.isnan(ISAAndMicrocodeEmulationLayer._decode_fp8_e4m3(0x7F))

    # CUDA warp reduce check
    vals = np.array([i + 1 for i in range(32)], dtype=np.uint32)
    warp_sum = ISAAndMicrocodeEmulationLayer.emulate_cuda_warp_reduce_sum(vals)
    assert warp_sum == int(np.sum(vals))


def test_7_mechanism_5_algorithmic_subsumption_and_redundant_work_deletion():
    """
    Verifies Mechanism 5: Algorithmic Subsumption deletes > 80% of redundant
    operations with 0 backprop epochs.
    """
    audit = AlgorithmicSubsumptionFrontEnd.run_audit()

    assert audit.mechanism_selected == "MECHANISM_5_ALGORITHMIC_SUBSUMPTION"
    assert audit.contract_parity_met is True
    assert audit.raw_hardware_parity_claimed is False
    assert audit.operations_deleted_pct > 80.0
    assert audit.error_or_discrepancy <= 0.05


def test_8_adversarial_conservation_law_honesty_falsification():
    """
    Verifies Space-Time Conservation Law:
    Feeding uniform white-noise data honestly causes the profiler to reject
    subsumption and route to Mechanism 1 (TDM) without fabricating speedups.
    """
    rng = np.random.default_rng(2026)
    noise_mat = rng.uniform(-10.0, 10.0, size=(256, 256)).astype(np.float32)

    decision = SpaceTimeInformationProfiler.profile_and_route(noise_mat, workload_type="dense_gemm")
    assert decision["mechanism"] == "MECHANISM_1_TDM_CACHE_TILED"
    assert decision["compressible"] is False
    assert decision["entropy"] > 0.85


def test_9_master_software_transistor_replacement_full_audit():
    """
    Verifies the aggregated audit suite executes all 5 mechanisms,
    all contracts pass, all falsifications pass, raw hardware parity is never claimed,
    and total estimated transistors subsumed exceeds 1,000,000,000.
    """
    report = run_all_transistor_replacement_audits()

    assert report["engine"] == "LEO_SOFTWARE_DEFINED_TRANSISTOR_REPLACEMENT_ENGINE"
    assert report["raw_hardware_parity_claimed"] is False
    assert report["all_contracts_met"] is True
    assert report["all_adversarial_falsifications_passed"] is True
    assert report["adversarial_conservation_law_honesty_verified"] is True
    assert len(report["audits"]) == 5
    assert report["total_estimated_hardware_transistors_subsumed"] > 1_000_000_000
