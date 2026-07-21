"""
core_ai/low_rank_adapter.py
Low-Rank Factorization (SVD) module for linear layer weight compression.
Factorizes dense Linear weight W (in x out) into A (in x r) and B (r x out).
"""

import torch
import torch.nn as nn
import time
from typing import Tuple, Dict, Any

class LowRankLinear(nn.Module):
    """
    Factorizes a dense Linear layer into two lower-rank matrices (A and B).
    W ~ A @ B where A is (in_features x rank) and B is (rank x out_features).
    """
    def __init__(self, in_features: int, out_features: int, rank: int = 16, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank

        self.factor_A = nn.Parameter(torch.zeros(in_features, rank))
        self.factor_B = nn.Parameter(torch.zeros(rank, out_features))

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter('bias', None)

    @classmethod
    def from_dense(cls, dense_layer: nn.Linear, rank: int = 16) -> 'LowRankLinear':
        """Constructs a LowRankLinear layer from a dense layer using SVD."""
        instance = cls(dense_layer.in_features, dense_layer.out_features, rank=rank, bias=dense_layer.bias is not None)
        
        with torch.no_grad():
            # Perform Singular Value Decomposition
            weight = dense_layer.weight.data.float()
            # weight shape in PyTorch is (out_features, in_features)
            U, S, Vh = torch.linalg.svd(weight, full_matrices=False)
            
            # Truncate to desired rank
            r = min(rank, S.shape[0])
            U_r = U[:, :r]
            S_r = torch.diag(torch.sqrt(S[:r]))
            Vh_r = Vh[:r, :]
            
            # Reconstruct factor matrices matching (in_features, r) and (r, out_features)
            # W = U S Vh => W_approx = (U_r sqrt(S_r)) (sqrt(S_r) Vh_r)
            # Output: y = x W^T = x (B^T A^T) = (x @ B^T) @ A^T
            # So factor_A is (in_features, r), factor_B is (r, out_features)
            mat_A = (Vh_r.T @ S_r)   # (in_features, r)
            mat_B = (S_r @ U_r.T)   # (r, out_features)
            
            instance.factor_A.copy_(mat_A)
            instance.factor_B.copy_(mat_B)
            
            if dense_layer.bias is not None:
                instance.bias.copy_(dense_layer.bias.data)
                
        return instance

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Two smaller matrix multiplications: x @ A -> intermediate @ B
        h = torch.matmul(x, self.factor_A)
        out = torch.matmul(h, self.factor_B)
        if self.bias is not None:
            out += self.bias
        return out


def compare_dense_vs_low_rank(
    in_features: int = 4096,
    out_features: int = 4096,
    rank: int = 128,
    batch_size: int = 1,
    seq_len: int = 128,
    iterations: int = 50
) -> Dict[str, Any]:
    """
    Benchmarks memory usage, FLOPs reduction, and execution latency
    between a standard dense Linear layer and a Low-Rank SVD layer.
    """
    dense_layer = nn.Linear(in_features, out_features)
    low_rank_layer = LowRankLinear.from_dense(dense_layer, rank=rank)

    x = torch.randn(batch_size, seq_len, in_features)

    # Warmup
    for _ in range(5):
        _ = dense_layer(x)
        _ = low_rank_layer(x)

    # Benchmark Dense
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = dense_layer(x)
    dense_latency_ms = (time.perf_counter() - t0) / iterations * 1000.0

    # Benchmark Low-Rank
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = low_rank_layer(x)
    low_rank_latency_ms = (time.perf_counter() - t0) / iterations * 1000.0

    dense_params = in_features * out_features
    low_rank_params = (in_features * rank) + (rank * out_features)
    param_reduction_pct = (1.0 - (low_rank_params / dense_params)) * 100.0

    return {
        "in_features": in_features,
        "out_features": out_features,
        "rank": rank,
        "dense_params": dense_params,
        "low_rank_params": low_rank_params,
        "param_reduction_pct": round(param_reduction_pct, 2),
        "dense_latency_ms": round(dense_latency_ms, 3),
        "low_rank_latency_ms": round(low_rank_latency_ms, 3),
        "speedup_multiplier": round(dense_latency_ms / max(1e-6, low_rank_latency_ms), 2)
    }
