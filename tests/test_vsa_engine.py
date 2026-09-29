"""
tests/test_vsa_engine.py
========================
Unit tests for the Vector Symbolic Architecture (VSA) Engine.
Verifies continuous-to-hyperdimensional projection, bitwise XOR binding,
in-register popcount Hamming distance, and majority bundling.
"""

import numpy as np
import pytest

from hyper.research_engine.vsa_bridge import VSAEngine


def test_vsa_projection_shape_and_type():
    in_dim = 64
    out_bits = 8192
    basis = VSAEngine.generate_random_basis(in_dim, out_bits, seed=123)
    assert basis.shape == (out_bits, in_dim)
    assert basis.dtype == np.float32

    x = np.random.randn(in_dim).astype(np.float32)
    x /= np.linalg.norm(x)
    hv = VSAEngine.project(x, basis)

    assert isinstance(hv, np.ndarray)
    assert hv.dtype == np.uint32
    assert len(hv) == out_bits // 32


def test_vsa_binding_involutory_property():
    """Binding an element with itself yields zero (identity): A XOR A = 0."""
    in_dim = 64
    basis = VSAEngine.generate_random_basis(in_dim, 8192)
    x = np.random.randn(in_dim).astype(np.float32)
    a = VSAEngine.project(x, basis)

    identity = VSAEngine.bind(a, a)
    assert np.all(identity == 0)


def test_vsa_binding_preserves_quasi_orthogonality():
    """A XOR B is quasi-orthogonal to both A and B in 8192-dimensional space (d_H ~ 4096)."""
    in_dim = 64
    basis = VSAEngine.generate_random_basis(in_dim, 8192)
    a = VSAEngine.project(np.random.randn(in_dim).astype(np.float32), basis)
    b = VSAEngine.project(np.random.randn(in_dim).astype(np.float32), basis)

    bound = VSAEngine.bind(a, b)
    d_ha = VSAEngine.hamming_distance(bound, a)
    d_hb = VSAEngine.hamming_distance(bound, b)

    # 8192 / 2 = 4096. Standard deviation for binomial(8192, 0.5) is ~45.2
    # Within 5 standard deviations: 4096 +/- 250
    assert abs(d_ha - 4096) < 250
    assert abs(d_hb - 4096) < 250


def test_vsa_hamming_distance_exactness():
    # Construct synthetic 8192-bit vectors with known differing bits
    u32_len = 8192 // 32
    a = np.zeros(u32_len, dtype=np.uint32)
    b = np.zeros(u32_len, dtype=np.uint32)

    # Set 7 bits in b
    b[0] = 0b1010101  # 4 bits set
    b[1] = 0b111      # 3 bits set

    dist = VSAEngine.hamming_distance(a, b)
    assert dist == 7


def test_vsa_gemm_surrogate_cosine_fidelity():
    """Verifies that pairwise Hamming distance closely matches true cosine similarity."""
    in_dim = 128
    out_bits = 8192
    basis = VSAEngine.generate_random_basis(in_dim, out_bits, seed=42)

    x1 = np.random.randn(in_dim).astype(np.float32)
    x1 /= np.linalg.norm(x1)

    # Correlated vector with high cosine similarity
    x2 = x1 + np.random.randn(in_dim).astype(np.float32) * 0.15
    x2 /= np.linalg.norm(x2)
    true_cos = float(np.dot(x1, x2))

    b1 = VSAEngine.project(x1, basis)
    b2 = VSAEngine.project(x2, basis)

    codebook = np.stack([b2], axis=0)
    sims = VSAEngine.gemm_surrogate(b1, codebook)
    est_cos = float(sims[0])

    # Error under Johnson-Lindenstrauss with D=8192 is typically < 0.03
    error = abs(true_cos - est_cos)
    assert error < 0.05, f"Expected cosine error < 0.05, got {error:.4f} (True: {true_cos:.4f}, Est: {est_cos:.4f})"


def test_vsa_majority_bundling():
    """Majority vote across vectors preserves shared bit features."""
    u32_len = 8192 // 32
    v1 = np.zeros(u32_len, dtype=np.uint32)
    v2 = np.zeros(u32_len, dtype=np.uint32)
    v3 = np.zeros(u32_len, dtype=np.uint32)

    # Shared features between v1 and v2
    v1[0] = 0xFFFFFFFF
    v2[0] = 0xFFFFFFFF
    v3[0] = 0x00000000

    consensus = VSAEngine.bundle([v1, v2, v3])
    # Word 0 should be 1s because 2/3 voted 1
    assert consensus[0] == 0xFFFFFFFF
    # Remaining words should be 0s
    assert np.all(consensus[1:] == 0)


def test_vsa_pin_to_pcores_safe_call():
    # Calling pin_to_pcores should execute without exceptions on all systems
    VSAEngine.pin_to_pcores()
