"""
tests/test_vsa_10k_engine.py
============================
Unit tests for the 10,000-Bit Vector Symbolic Architecture (VSA) Engine.
Validates AVX2 XOR binding, popcount bundling, and Charikar cosine mapping.
"""

import numpy as np
import pytest

from hyper.research_engine.vsa_bridge import VSAEngine


def test_vsa_10k_projection_and_distance():
    # 10,000-bit hypervectors
    dim = 10000
    in_dim = 128
    basis = VSAEngine.generate_random_basis(in_dim=in_dim, out_bits=dim, seed=1337)

    # Similar inputs (cosine angle ~ 0)
    x1 = np.ones(in_dim, dtype=np.float32)
    x2 = np.ones(in_dim, dtype=np.float32) + 0.05 * np.random.randn(in_dim).astype(np.float32)

    hv1 = VSAEngine.project(x1, basis)
    hv2 = VSAEngine.project(x2, basis)

    dist = VSAEngine.hamming_distance(hv1, hv2)
    # Similar inputs should have small Hamming distance relative to 10,000 bits
    assert dist < 1500  # < 15% bit difference

    # Orthogonal input
    x_orth = np.zeros(in_dim, dtype=np.float32)
    x_orth[0] = 1.0
    x_orth[1] = -1.0
    hv_orth = VSAEngine.project(x_orth, basis)
    dist_orth = VSAEngine.hamming_distance(hv1, hv_orth)
    # Orthogonal hypervectors should concentrate around D / 2 = 5,000 bits
    assert 4000 < dist_orth < 6000


def test_vsa_10k_binding_properties():
    # Binding must be self-inverting: (A XOR B) XOR B == A
    dim = 10000
    in_dim = 64
    basis = VSAEngine.generate_random_basis(in_dim=in_dim, out_bits=dim, seed=42)

    a = VSAEngine.project(np.random.randn(in_dim).astype(np.float32), basis)
    b = VSAEngine.project(np.random.randn(in_dim).astype(np.float32), basis)

    bound = VSAEngine.bind(a, b)
    unbound = VSAEngine.bind(bound, b)

    assert np.array_equal(unbound, a)
    assert VSAEngine.hamming_distance(unbound, a) == 0


def test_vsa_10k_charikar_cosine():
    # Charikar isomorphism: cos(pi * d_H / D)
    dim = 10000
    in_dim = 64
    basis = VSAEngine.generate_random_basis(in_dim=in_dim, out_bits=dim, seed=100)

    # Identical
    x = np.random.randn(in_dim).astype(np.float32)
    x = x / np.linalg.norm(x)
    hv = VSAEngine.project(x, basis)

    # Codebook with x and orthogonal y
    y = np.random.randn(in_dim).astype(np.float32)
    y = y - np.dot(x, y) * x  # Gram-Schmidt orthogonalize
    y = y / np.linalg.norm(y)
    hv_y = VSAEngine.project(y, basis)

    codebook = np.stack([hv, hv_y], axis=0)
    sims = VSAEngine.gemm_surrogate(hv, codebook)

    assert len(sims) == 2
    # Self similarity must be 1.0 (Hamming distance 0)
    assert pytest.approx(1.0, abs=1e-3) == sims[0]
    # Orthogonal similarity must be near 0.0 (Hamming distance ~ 5,000)
    assert pytest.approx(0.0, abs=0.15) == sims[1]
