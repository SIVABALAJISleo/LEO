"""
tests/test_exact_omega_out_of_core_and_ptx.py

Verification Suite for 6-Stage EXACT-OMEGA Pathway & Lifter:
  - Hard Exactness Gate & Lossy Mode Blocker
  - Universal Canonical IR (CIR) Lifter for PTX Instruction Streams
  - Zero-Loss Escape Cascade (E-Graph Associativity & Binary Operator Squaring)
  - Out-Of-Core Virtual VRAM (4 KB Sector Direct I/O Lossless Bit-Plane Stream)
  - Deterministic Time-Division Multiplexing (TDM) Fallback
  - End-to-End Master EXACT-OMEGA Audit Closure
"""

import hashlib
import os
import sys
import tempfile
import pytest
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.canonical.exact_omega_router import (
    HardExactnessGate,
    UniversalCanonicalIRLifter,
    ZeroLossEscapeCascade,
    OutOfCoreVirtualVRAM,
    ExactSiliconExecutor,
    ExactOracleVerifier,
    ExactOmegaRouter,
    run_exact_omega_verification_suite,
)


def test_hard_exactness_gate_blocks_lossy_modes():
    """Verify Stage 1 strictly blocks any lossy quantization or pruning."""
    # 1. Exact mode false must be rejected
    with pytest.raises(ValueError, match="HARD EXACTNESS GATE REJECTION"):
        HardExactnessGate.validate_workload_mode(exact_mode=False)

    # 2. Lossy allowed must be rejected
    with pytest.raises(ValueError, match="HARD EXACTNESS GATE REJECTION"):
        HardExactnessGate.validate_workload_mode(exact_mode=True, lossy_allowed=True)

    # 3. Clean exact mode succeeds
    res_f32 = HardExactnessGate.validate_workload_mode(exact_mode=True, dtype="float32")
    assert res_f32["gate_passed"] is True
    assert res_f32["exact_mode_locked"] is True
    assert res_f32["certified_tolerance"] <= 1e-6

    res_int = HardExactnessGate.validate_workload_mode(exact_mode=True, dtype="int32")
    assert res_int["certified_tolerance"] == 0.0


def test_universal_cir_ptx_lifter_and_execution():
    """Verify Stage 2 & 5: Lift PTX assembly into CIR and execute with exact IEEE-754 semantics."""
    ptx_code = """
    // CUDA PTX Kernel for FMA and Warp Reduction
    ld.global.f32 %f1, [%rd1];
    ld.global.f32 %f2, [%rd2];
    ld.global.f32 %f0, [%rd0];
    fma.rn.f32 %f3, %f1, %f2, %f0;
    shfl.sync.bfly.b32 %f4, %f3, 16, 0x1f, 0xffffffff;
    st.global.f32 [%rd3], %f4;
    """
    ops = UniversalCanonicalIRLifter.lift_ptx_instruction_block(ptx_code)
    assert len(ops) >= 5
    assert any(op.op_type == "FMA" for op in ops)
    assert any(op.op_type == "WARP_SHUFFLE_BF_REDUCE" for op in ops)

    rng = np.random.default_rng(777)
    n = 64
    a = rng.standard_normal(n).astype(np.float32)
    b = rng.standard_normal(n).astype(np.float32)
    c = rng.standard_normal(n).astype(np.float32)

    symbol_table = {"%rd1": a, "%rd2": b, "%rd0": c}
    out_table = ExactSiliconExecutor.execute_cir_ptx_block(ops, symbol_table)

    # Verify exact numerical output against pure reference
    fma_ref = a * b + c
    reshaped = fma_ref.reshape(-1, 32)
    reduced = reshaped.sum(axis=1, keepdims=True)
    expected_f4 = np.repeat(reduced, 32).reshape(fma_ref.shape)

    actual_f4 = out_table["%f4"]
    assert np.array_equal(actual_f4, expected_f4)
    assert float(np.max(np.abs(actual_f4 - expected_f4))) == 0.0


def test_zero_loss_escape_egraph_and_memoization():
    """Verify Stage 3: E-Graph Associativity (A @ B) @ v -> A @ (B @ v) with 0.0 error."""
    rng = np.random.default_rng(888)
    dim = 128
    A = rng.standard_normal((dim, dim)).astype(np.float32)
    B = rng.standard_normal((dim, dim)).astype(np.float32)
    v = rng.standard_normal((dim, 1)).astype(np.float32)

    cascade = ZeroLossEscapeCascade()
    res, bypassed, base_flops, exec_flops = cascade.try_egraph_associativity_rewrite(A, B, v)

    assert bypassed is True
    assert base_flops > exec_flops
    # Calculate exact unoptimized reference: (A @ B) @ v
    ref = ((A.astype(np.float64) @ B.astype(np.float64)) @ v.astype(np.float64)).astype(np.float32)
    assert np.array_equal(res, ref)
    assert float(np.max(np.abs(res - ref))) == 0.0

    # Test SHA-256 Memoization Cache
    raw_v = v.tobytes()
    cascade.memo_store("ASSOCIATIVE_OP", raw_v, res)
    cached = cascade.memo_lookup("ASSOCIATIVE_OP", raw_v)
    assert cached is not None
    assert np.array_equal(cached, res)


def test_zero_loss_binary_operator_squaring_wormhole():
    """Verify Stage 3: Direct Closed-Form Binary Operator Squaring solves T steps in log2(T)."""
    rng = np.random.default_rng(999)
    dim = 8
    # Construct stable matrix (spectral radius < 1)
    A = (rng.standard_normal((dim, dim)) / np.sqrt(dim) * 0.9).astype(np.float32)
    b = rng.standard_normal(dim).astype(np.float32)
    x0 = rng.standard_normal(dim).astype(np.float32)

    total_steps = 1024
    res_jump, bypassed, base_flops, exec_flops = ZeroLossEscapeCascade.try_binary_operator_squaring_jump(
        A, b, x0, total_steps_T=total_steps
    )
    assert bypassed is True
    assert exec_flops < base_flops

    # Compute naive sequential ground truth
    x_curr = x0.astype(np.float64)
    for _ in range(total_steps):
        x_curr = A.astype(np.float64) @ x_curr + b.astype(np.float64)

    # Machine-precision FP32/FP64 bound (A was float32)
    err = float(np.max(np.abs(res_jump.astype(np.float64) - x_curr)))
    assert err < 1e-6, f"Binary operator squaring error {err} exceeds precision bound"


def test_out_of_core_nvme_virtual_vram_bit_identical_streaming():
    """Verify Stage 4: Out-Of-Core 4 KB-aligned lossless byte-plane streaming with 0.0 error."""
    tmp_dir = os.path.join(tempfile.gettempdir(), "hyper_test_ooc_vram")
    os.makedirs(tmp_dir, exist_ok=True)
    pack_path = os.path.join(tmp_dir, "test_layer_pack.bin")

    rng = np.random.default_rng(1234)
    # Realistic layer dimensions (e.g. 512 x 256 = 131,072 floats = 512 KB)
    W_orig = rng.standard_normal((512, 256)).astype(np.float32)

    manifest = OutOfCoreVirtualVRAM.encode_and_pack_tensor(W_orig, pack_path)
    assert manifest["sector_aligned"] is True
    assert manifest["padded_len"] % 4096 == 0
    assert manifest["codec_type"] == 100

    W_rec = OutOfCoreVirtualVRAM.stream_and_reconstruct_tensor(manifest)

    # Assert 100% bitwise identity
    assert np.array_equal(W_rec, W_orig), "Reconstructed tensor does not match original bits"
    assert float(np.max(np.abs(W_rec - W_orig))) == 0.0
    assert hashlib.sha256(W_rec.tobytes()).hexdigest() == manifest["sha256"]

    try:
        if os.path.exists(pack_path):
            os.remove(pack_path)
    except Exception:
        pass


def test_deterministic_tdm_dense_gemm_fallback():
    """Verify Stage 5: Deterministic TDM fallback executes dense GEMM with 100% exact parity."""
    rng = np.random.default_rng(5678)
    dim = 128
    A = rng.standard_normal((dim, dim)).astype(np.float32)
    B = rng.standard_normal((dim, dim)).astype(np.float32)

    C_tdm, telemetry = ExactSiliconExecutor.execute_deterministic_tdm_dense_gemm(A, B, tile_size=32)

    C_ref = (A.astype(np.float64) @ B.astype(np.float64)).astype(np.float32)
    assert np.array_equal(C_tdm, C_ref)
    assert float(np.max(np.abs(C_tdm - C_ref))) == 0.0
    assert telemetry["decision_rule_d2"] == "NO_BYPASS_HONEST_TIME_MULTIPLEXING"
    assert telemetry["total_tiles_processed"] > 0


def test_master_exact_omega_verification_suite():
    """Verify Stage 6: Master verification suite emits certified SHA-256 sealed receipts."""
    report = run_exact_omega_verification_suite()

    assert report["all_exact_computational_parity"] is True
    assert report["all_ulp_bounds_met"] is True
    assert report["raw_hardware_parity_never_claimed"] is True
    assert report["total_receipts"] == 4

    for r in report["receipts"]:
        assert r["exact_computational_parity"] is True
        assert r["contract_parity_met"] is True
        assert r["fidelity_contract"] == "EXACT_MATHEMATICAL_PARITY"
        assert len(r["sha256_output_seal"]) == 64
        assert r["raw_hardware_parity_claimed"] is False
        assert r["exactness_certified"] is True
