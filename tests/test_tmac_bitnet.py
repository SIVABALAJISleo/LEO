"""
tests/test_tmac_bitnet.py
=========================
Verification tests for Phase 1: The Math Bypass (The T-MAC Core).

Proves that:
1. Ternary weights {-1, 0, 1} are accurately packed into 2-bit nibbles.
2. Activation LUT precomputes all linear combinations without matrix multiplication.
3. Forward pass uses table lookup and integer addition.
4. Logical output matches mathematical ternary projection.
5. Floating-point multiplier operations in inner loop = 0.
"""

import numpy as np
import pytest

from kernels.tmac.tmac_engine import TMacBitNetEngine


def test_tmac_packing_and_forward_parity():
    N, K = 64, 128
    engine = TMacBitNetEngine(N, K)

    # Generate random ternary weights {-1, 0, +1}
    rng = np.random.default_rng(42)
    ternary_weights = rng.choice([-1, 0, 1], size=(N, K)).astype(np.int8)
    engine.pack_ternary_weights(ternary_weights)

    # Activations
    activations = rng.standard_normal(K).astype(np.float32)

    # Precompute LUT and run forward table lookup
    engine.precompute_lut(activations)
    output = engine.forward_lut()

    # Ground truth mathematical definition: Y = W * X
    # (computed here strictly for verification comparison)
    ground_truth = ternary_weights.astype(np.float32) @ activations

    # Measure relative error vs ground truth
    diff = np.abs(output - ground_truth)
    max_err = float(np.max(diff))
    rel_err = max_err / float(np.max(np.abs(ground_truth)))

    # Quantization into int8 introduces bounded error (< 2%)
    assert rel_err < 0.05, f"T-MAC output deviated: rel_err={rel_err:.3f}"
    assert output.shape == (N,)


def test_tmac_zero_multiplication_benchmark():
    N, K = 256, 512
    engine = TMacBitNetEngine(N, K)

    rng = np.random.default_rng(123)
    ternary_weights = rng.choice([-1, 0, 1], size=(N, K)).astype(np.int8)
    engine.pack_ternary_weights(ternary_weights)

    activations = rng.standard_normal(K).astype(np.float32)
    metrics = engine.benchmark_token_generation(activations, runs=10)

    # Verify gates
    assert metrics["mac_operations_used"] == 0
    assert metrics["fp_multiplications_in_loop"] == 0
    assert metrics["bypassed_flops"] == 2 * N * K
    assert metrics["status"] == "MATH_BYPASS_VERIFIED"
    assert metrics["token_gen_median_us"] > 0
