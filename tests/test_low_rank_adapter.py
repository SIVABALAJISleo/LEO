"""
tests/test_low_rank_adapter.py
Unit tests for Low-Rank SVD layer decomposition and comparative benchmarks.
"""

import pytest
import torch
import torch.nn as nn
from core_ai.low_rank_adapter import LowRankLinear, compare_dense_vs_low_rank

def test_low_rank_linear_forward():
    in_features, out_features, rank = 128, 256, 16
    dense = nn.Linear(in_features, out_features)
    low_rank = LowRankLinear.from_dense(dense, rank=rank)

    x = torch.randn(2, 32, in_features)
    out_dense = dense(x)
    out_low_rank = low_rank(x)

    assert out_low_rank.shape == (2, 32, out_features)
    assert out_low_rank.shape == out_dense.shape

def test_compare_dense_vs_low_rank():
    results = compare_dense_vs_low_rank(
        in_features=256,
        out_features=256,
        rank=16,
        iterations=5
    )
    assert "param_reduction_pct" in results
    assert results["param_reduction_pct"] > 80.0
    assert "speedup_multiplier" in results
