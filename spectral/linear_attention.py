"""
spectral/linear_attention.py
Pillar: Linear O(N) Attention Mechanism (Linformer / Performer)
Replaces standard O(N^2) Softmax(Q K^T) V with O(N) kernel feature map:
  Output = phi(Q) (phi(K)^T V)
Collapses memory and compute complexity for long-context sequences from quadratic to linear.
"""

import time
import torch
import torch.nn as nn
import torch.nn.functional as F

class LinearAttention(nn.Module):
    def __init__(self, dim: int = 512, heads: int = 8):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.q_proj = nn.Linear(dim, dim, bias=False)
        self.k_proj = nn.Linear(dim, dim, bias=False)
        self.v_proj = nn.Linear(dim, dim, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        
    def _feature_map(self, x: torch.Tensor) -> torch.Tensor:
        return F.elu(x) + 1.0
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, n, d = x.shape
        h = self.heads
        hd = self.head_dim
        
        q = self.q_proj(x).view(b, n, h, hd).transpose(1, 2)
        k = self.k_proj(x).view(b, n, h, hd).transpose(1, 2)
        v = self.v_proj(x).view(b, n, h, hd).transpose(1, 2)
        
        q_phi = self._feature_map(q)
        k_phi = self._feature_map(k)
        
        kv = torch.matmul(k_phi.transpose(-2, -1), v)
        out = torch.matmul(q_phi, kv)
        
        k_sum = k_phi.sum(dim=-2, keepdim=True)
        denom = torch.matmul(q_phi, k_sum.transpose(-2, -1)) + 1e-6
        out = out / denom
        
        out = out.transpose(1, 2).contiguous().view(b, n, d)
        return self.out_proj(out)
