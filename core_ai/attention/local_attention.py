"""
core_ai/attention/local_attention.py
Radical Pathway Redesign: Local Attention and Vectorized Block Attention for LEO.
Optimized for Intel Core i5-12450H + Intel UHD architecture.

Eliminates O(n^2) full attention in favor of:
1. Local Attention (Sliding Window, O(n * w))
2. Vectorized Block Attention with Past Top-K Summary (O(n * b + b^2))
3. PyTorch drop-in module LocalBlockAttentionModule for neural pipelines
"""

import time
import math
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class BlockAttentionResult:
    output: np.ndarray
    time_ms: float
    speedup: float = 1.0
    error: float = 0.0
    tokens_processed: int = 0
    theoretical_flops: int = 0
    actual_flops: int = 0


class VectorizedBlockAttention:
    """
    Block attention using vectorized NumPy operations.
    Processes entire blocks at once, eliminating Python loop overhead.
    
    Architecture:
      Step 1: Intra-block dense attention (Q_block @ K_block.T)
      Step 2: Inter-block summary attention using top-K salient keys/values from past
      Step 3: Adaptive weighting between local and summary representations
    """
    
    def __init__(self, block_size: int = 64, summary_size: int = 20, causal: bool = True):
        self.block_size = max(1, int(block_size))
        self.summary_size = max(1, int(summary_size))
        self.causal = causal

    @staticmethod
    def softmax_stable(x: np.ndarray, axis: int = -1) -> np.ndarray:
        """Numerically stable softmax handling extreme dynamic ranges."""
        x_max = np.max(x, axis=axis, keepdims=True)
        # Prevent NaN when all elements are -inf
        x_shifted = x - x_max
        exp_x = np.exp(x_shifted)
        sum_exp = np.sum(exp_x, axis=axis, keepdims=True)
        # Avoid division by zero
        sum_exp = np.maximum(sum_exp, 1e-12)
        return exp_x / sum_exp

    def forward(self, Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
        """
        Block attention forward pass using vectorized operations.
        
        Args:
            Q, K, V: ndarray of shape (seq_len, d) or (batch, seq_len, d)
        Returns:
            output: ndarray of shape matching Q
        """
        if Q.ndim == 3:
            # Batch processing
            batch_size = Q.shape[0]
            outs = [self.forward(Q[b], K[b], V[b]) for b in range(batch_size)]
            return np.stack(outs, axis=0)

        seq_len, d = Q.shape
        output = np.zeros_like(Q)
        block_size = self.block_size
        scale = 1.0 / np.sqrt(d)

        # Process sequence block by block
        for block_idx in range(0, seq_len, block_size):
            block_start = block_idx
            block_end = min(block_idx + block_size, seq_len)
            block_len = block_end - block_start

            # Extract block queries, keys, values
            Q_block = Q[block_start:block_end]  # (block_len, d)
            K_block = K[block_start:block_end]  # (block_len, d)
            V_block = V[block_start:block_end]  # (block_len, d)

            # Step 1: Intra-block attention
            scores_local = (Q_block @ K_block.T) * scale  # (block_len, block_len)

            if self.causal:
                # Apply causal mask within block
                causal_mask = np.triu(np.ones((block_len, block_len), dtype=bool), k=1)
                scores_local = np.where(causal_mask, -1e9, scores_local)

            attn_local = self.softmax_stable(scores_local, axis=-1)  # (block_len, block_len)
            output_local = attn_local @ V_block                      # (block_len, d)

            # Step 2: Inter-block attention (past tokens only)
            if block_start > 0:
                K_past = K[:block_start]  # (past_len, d)
                V_past = V[:block_start]

                # Salience scoring via L2-norm product
                k_norm = np.linalg.norm(K_past, axis=1)
                v_norm = np.linalg.norm(V_past, axis=1)
                importance = k_norm * v_norm

                # Select top-K summary tokens
                k_count = min(self.summary_size, len(importance))
                top_k_indices = np.argsort(importance)[-k_count:]

                K_summary = K_past[top_k_indices]  # (k_count, d)
                V_summary = V_past[top_k_indices]  # (k_count, d)

                # Attention to summary
                scores_summary = (Q_block @ K_summary.T) * scale  # (block_len, k_count)
                attn_summary = self.softmax_stable(scores_summary, axis=-1)
                output_summary = attn_summary @ V_summary         # (block_len, d)

                # Step 3: Adaptive convex combination
                # Weight by maximum attention probability confidence
                w_local = np.mean(np.max(attn_local, axis=1, keepdims=True))
                w_summary = np.mean(np.max(attn_summary, axis=1, keepdims=True))
                w_total = w_local + w_summary + 1e-8

                output_block = (w_local * output_local + w_summary * output_summary) / w_total
            else:
                output_block = output_local

            output[block_start:block_end] = output_block

        return output

    def compute_flops(self, seq_len: int, d: int) -> Tuple[int, int]:
        """Returns (full_flops, block_flops)."""
        full_flops = 2 * (seq_len ** 2) * d + 2 * (seq_len ** 2) * d
        num_blocks = (seq_len + self.block_size - 1) // self.block_size
        intra_flops = num_blocks * (4 * (self.block_size ** 2) * d)
        inter_flops = seq_len * (4 * self.summary_size * d)
        block_flops = intra_flops + inter_flops
        return full_flops, block_flops


class LocalAttention:
    """
    Sliding window attention: each token attends only to neighbors within window_size.
    Complexity: O(n * w * d) where w << n, avoiding O(n^2 * d).
    """

    def __init__(self, window_size: int = 64, causal: bool = True):
        self.window_size = max(1, int(window_size))
        self.causal = causal

    @staticmethod
    def softmax_stable(x: np.ndarray, axis: int = -1) -> np.ndarray:
        x_max = np.max(x, axis=axis, keepdims=True)
        exp_x = np.exp(x - x_max)
        sum_exp = np.sum(exp_x, axis=axis, keepdims=True)
        return exp_x / np.maximum(sum_exp, 1e-12)

    def forward(self, Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
        """
        Local window attention forward pass.
        
        Args:
            Q, K, V: (seq_len, d) or (batch, seq_len, d)
        """
        if Q.ndim == 3:
            batch_size = Q.shape[0]
            outs = [self.forward(Q[b], K[b], V[b]) for b in range(batch_size)]
            return np.stack(outs, axis=0)

        seq_len, d = Q.shape
        w = self.window_size
        scale = 1.0 / np.sqrt(d)
        output = np.zeros_like(Q)

        for i in range(seq_len):
            if self.causal:
                start = max(0, i - w)
                end = i + 1
            else:
                start = max(0, i - w)
                end = min(seq_len, i + w + 1)

            q_i = Q[i:i + 1]        # (1, d)
            K_local = K[start:end]  # (window_len, d)
            V_local = V[start:end]  # (window_len, d)

            scores = (q_i @ K_local.T) * scale
            attn = self.softmax_stable(scores, axis=-1)
            output[i] = (attn @ V_local).ravel()

        return output

    def compute_flops(self, seq_len: int, d: int) -> Tuple[int, int]:
        full_flops = 4 * (seq_len ** 2) * d
        w = self.window_size
        local_flops = 4 * seq_len * min(w, seq_len) * d
        return full_flops, local_flops


if TORCH_AVAILABLE:
    class LocalBlockAttentionModule(nn.Module):
        """
        PyTorch drop-in module for Transformer layers.
        Supports Local Window and Block Attention with Top-K Salience.
        """
        def __init__(
            self,
            hidden_dim: int,
            num_heads: int = 8,
            mode: str = "block",
            block_size: int = 64,
            summary_size: int = 20,
            window_size: int = 64,
            causal: bool = True
        ):
            super().__init__()
            self.hidden_dim = hidden_dim
            self.num_heads = num_heads
            self.head_dim = hidden_dim // num_heads
            self.mode = mode
            self.block_size = block_size
            self.summary_size = summary_size
            self.window_size = window_size
            self.causal = causal
            self.scale = 1.0 / math.sqrt(self.head_dim)

            self.q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
            self.k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
            self.v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
            self.out_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)

        def forward(
            self,
            hidden_states: torch.Tensor,
            attention_mask: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
            """
            Args:
                hidden_states: (batch_size, seq_len, hidden_dim)
            Returns:
                out: (batch_size, seq_len, hidden_dim)
            """
            batch_size, seq_len, _ = hidden_states.shape

            Q = self.q_proj(hidden_states)
            K = self.k_proj(hidden_states)
            V = self.v_proj(hidden_states)

            # Reshape for multi-head: (batch, num_heads, seq_len, head_dim)
            Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
            K = K.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
            V = V.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

            if self.mode == "dense" or seq_len <= self.block_size:
                # Standard dense attention
                scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
                if self.causal:
                    mask = torch.triu(torch.ones(seq_len, seq_len, device=scores.device, dtype=torch.bool), diagonal=1)
                    scores = scores.masked_fill(mask, -1e9)
                attn = F.softmax(scores, dim=-1)
                context = torch.matmul(attn, V)
            elif self.mode == "local":
                # Sliding window attention
                context = torch.zeros_like(Q)
                w = self.window_size
                for i in range(seq_len):
                    start = max(0, i - w) if self.causal else max(0, i - w)
                    end = i + 1 if self.causal else min(seq_len, i + w + 1)
                    q_i = Q[:, :, i:i+1, :]
                    k_local = K[:, :, start:end, :]
                    v_local = V[:, :, start:end, :]
                    scores = torch.matmul(q_i, k_local.transpose(-2, -1)) * self.scale
                    attn = F.softmax(scores, dim=-1)
                    context[:, :, i:i+1, :] = torch.matmul(attn, v_local)
            else:
                # Block attention with top-K summaries
                context = torch.zeros_like(Q)
                b_size = self.block_size
                for b_idx in range(0, seq_len, b_size):
                    b_start = b_idx
                    b_end = min(b_idx + b_size, seq_len)
                    b_len = b_end - b_start

                    Q_b = Q[:, :, b_start:b_end, :]
                    K_b = K[:, :, b_start:b_end, :]
                    V_b = V[:, :, b_start:b_end, :]

                    scores_local = torch.matmul(Q_b, K_b.transpose(-2, -1)) * self.scale
                    if self.causal:
                        mask = torch.triu(torch.ones(b_len, b_len, device=scores_local.device, dtype=torch.bool), diagonal=1)
                        scores_local = scores_local.masked_fill(mask, -1e9)
                    attn_local = F.softmax(scores_local, dim=-1)
                    out_local = torch.matmul(attn_local, V_b)

                    if b_start > 0:
                        K_past = K[:, :, :b_start, :]
                        V_past = V[:, :, :b_start, :]

                        # Salience norm
                        importance = torch.norm(K_past, dim=-1) * torch.norm(V_past, dim=-1)
                        # Mean across batch and heads for unified index
                        imp_score = importance.mean(dim=(0, 1))
                        k_count = min(self.summary_size, b_start)
                        _, top_indices = torch.topk(imp_score, k_count)

                        K_sum = K_past[:, :, top_indices, :]
                        V_sum = V_past[:, :, top_indices, :]

                        scores_sum = torch.matmul(Q_b, K_sum.transpose(-2, -1)) * self.scale
                        attn_sum = F.softmax(scores_sum, dim=-1)
                        out_sum = torch.matmul(attn_sum, V_sum)

                        w_loc = attn_local.max(dim=-1, keepdim=True)[0].mean(dim=-2, keepdim=True)
                        w_sm = attn_sum.max(dim=-1, keepdim=True)[0].mean(dim=-2, keepdim=True)
                        w_tot = w_loc + w_sm + 1e-8

                        out_block = (w_loc * out_local + w_sm * out_sum) / w_tot
                    else:
                        out_block = out_local

                    context[:, :, b_start:b_end, :] = out_block

            # Merge heads
            context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_dim)
            return self.out_proj(context)
else:
    class LocalBlockAttentionModule:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required to use LocalBlockAttentionModule.")
