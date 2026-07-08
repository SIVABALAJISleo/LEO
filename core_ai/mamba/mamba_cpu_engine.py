"""
LEO AI V42 - The Irrelevance Engine
Phase 3: Mamba O(n) + Speculative Decoding Stack

CPU-optimized Mamba (State Space Model) implementation.
Replaces O(n^2) Attention with O(n) selective state spaces for infinite-context
linear processing on consumer hardware.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class MambaCPULayer(nn.Module):
    """
    CPU-optimized Mamba SSM Block.
    Uses linear complexity selective state spaces rather than quadratic attention.
    """
    def __init__(self, d_model: int, d_state: int = 16, d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(self.expand * self.d_model)

        # Input projection
        self.in_proj = nn.Linear(self.d_model, self.d_inner * 2, bias=False)
        
        # 1D Convolution for local context
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            bias=True,
            kernel_size=d_conv,
            groups=self.d_inner,
            padding=d_conv - 1,
        )

        # Projections for SSM parameters: delta, B, C
        self.x_proj = nn.Linear(self.d_inner, self.d_state * 2 + 1, bias=False)
        self.dt_proj = nn.Linear(1, self.d_inner, bias=True)

        # S4D initialization for A
        A = torch.arange(1, self.d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        
        # Output projection
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=False)

    def forward(self, hidden_states: torch.Tensor):
        """
        hidden_states: (batch, seq_len, d_model)
        """
        batch, seq_len, _ = hidden_states.shape
        
        # 1. Input projection (split into x and z for SiLU gating)
        xz = self.in_proj(hidden_states)
        x, z = xz.chunk(2, dim=-1)
        
        # 2. 1D Convolution over sequence length
        x = x.transpose(1, 2) # (batch, d_inner, seq_len)
        x = self.conv1d(x)[:, :, :seq_len] # truncate padding
        x = x.transpose(1, 2)
        
        x = F.silu(x)
        
        # 3. SSM parameter projections
        x_proj = self.x_proj(x)
        delta, B, C = torch.split(x_proj, [1, self.d_state, self.d_state], dim=-1)
        
        delta = F.softplus(self.dt_proj(delta)) # (batch, seq_len, d_inner)
        
        # 4. CPU-Optimized Parallel Scan (Standard SSM formulation)
        # For CPU, we implement a vectorized naive scan to avoid custom CUDA kernels.
        # This is wrapped in torch.compile for JIT loop unrolling.
        A = -torch.exp(self.A_log.float()) # (d_inner, d_state)
        
        # Discretize continuous parameters
        deltaA = torch.exp(torch.einsum('b l d, d n -> b l d n', delta, A))
        deltaB_u = torch.einsum('b l d, b l n, b l d -> b l d n', delta, B, x)
        
        # Sequential scan
        # Note: In production CPU we'd use a prefix-sum associative scan here.
        # For memory efficiency, we iterate the sequence.
        out_ssm = self._cpu_scan(deltaA, deltaB_u, C)
        
        # Add D skip connection
        out = out_ssm + (x * self.D)
        
        # 5. Gating and output projection
        out = out * F.silu(z)
        out = self.out_proj(out)
        
        return out

    # We use torch.compile to optimize the sequential loop heavily on CPU
    @torch.compile(backend="aot_eager", fullgraph=False) # Fallback to CPU execution
    def _cpu_scan(self, deltaA, deltaB_u, C):
        batch, seq_len, d_inner, d_state = deltaA.shape
        out = torch.zeros((batch, seq_len, d_inner), device=deltaA.device, dtype=deltaA.dtype)
        state = torch.zeros((batch, d_inner, d_state), device=deltaA.device, dtype=deltaA.dtype)
        
        for i in range(seq_len):
            state = deltaA[:, i] * state + deltaB_u[:, i]
            out[:, i] = torch.einsum('b d n, b n -> b d', state, C[:, i])
            
        return out

class MambaCPUModel(nn.Module):
    """
    A full Mamba stack using CPU-optimized layers.
    """
    def __init__(self, vocab_size: int, d_model: int, n_layers: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([MambaCPULayer(d_model) for _ in range(n_layers)])
        self.norm_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.embedding.weight

    def forward(self, input_ids: torch.Tensor):
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = x + layer(x) # residual connection
        x = self.norm_f(x)
        return self.lm_head(x)
