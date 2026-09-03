"""
tests/test_hyper_v3_transforms.py
Unit tests for transformation passes: Algebraic, Loop, Sparse, Fusion, Factorization, and Algorithmic.
"""

import pytest
import numpy as np
from hyper_v3.transforms.algebraic import AlgebraicTransformer
from hyper_v3.transforms.loop import LoopTransformer
from hyper_v3.transforms.memory import MemoryTransformer
from hyper_v3.transforms.sparse import SparseTransformer
from hyper_v3.transforms.fusion import FusionTransformer
from hyper_v3.transforms.factorization import FactorizationTransformer
from hyper_v3.transforms.representation import RepresentationTransformer
from hyper_v3.transforms.algorithmic import AlgorithmicTransformer


def test_algebraic_and_loop_transforms():
    a = np.eye(4)
    b = np.random.randn(4, 4)
    is_id, res = AlgebraicTransformer.eliminate_identity_matmul(a, b)
    assert is_id is True
    assert np.allclose(res, b)

    tiles = LoopTransformer.get_optimal_gemm_tiles(512, 512, 512)
    assert tiles.tile_m > 0
    assert tiles.vector_width == 8


def test_sparse_and_fusion_transforms():
    mat = np.random.randn(8, 8)
    sp_2to4 = SparseTransformer.enforce_2_to_4_sparsity(mat)
    assert sp_2to4.shape == (8, 8)

    a = np.random.randn(4, 4)
    b = np.random.randn(4, 4)
    bias = np.ones((4, 4))
    fused_out = FusionTransformer.fused_gemm_bias_relu(a, b, bias)
    assert np.all(fused_out >= 0)


def test_factorization_and_algorithmic():
    mat = np.random.randn(32, 32)
    u, v = FactorizationTransformer.randomized_svd(mat, rank=8)
    assert u.shape == (32, 8)
    assert v.shape == (8, 32)

    q_w, gamma = FactorizationTransformer.bitnet_ternary_quantize(mat)
    assert set(np.unique(q_w)).issubset({-1, 0, 1})

    points = np.random.rand(10, 3) * 100.0
    morton = RepresentationTransformer.compute_morton_codes_3d(points)
    assert len(morton) == 10

    pos = np.random.randn(10, 3)
    mass = np.ones((10, 1))
    acc = AlgorithmicTransformer.barnes_hut_nbody_step(pos, mass)
    assert acc.shape == (10, 3)
