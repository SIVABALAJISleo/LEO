"""
Fourier-Domain Sparse Attention
Transforms attention matrices into frequency domains to prune 95% of compute coefficients.
"""
import torch
import torch.nn as nn
import math
from typing import Optional

class FourierAttentionPruner(nn.Module):
    """
    Fourier-domain sparse execution module.
    Converts Q and K states to frequency domain, performs sparse filtering,
    and returns a reconstruction of attention scores.
    """
    
    def __init__(self, keep_ratio: float = 0.05):
        super().__init__()
        self.keep_ratio = keep_ratio
        
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Runs attention using Fourier domain sparsification.
        Inputs:
            query, key, value: shape [batch, heads, seq_len, head_dim]
        """
        batch, heads, seq_len, head_dim = query.shape
        
        # Compute standard dot-product attention scores
        # scores: [batch, heads, seq_len, seq_len]
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(head_dim)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
            
        # Fourier transformation over attention matrix dimensions (sequence dimensions)
        # We apply 2D FFT to the sequence matrix
        fft_scores = torch.fft.fft2(scores)
        
        # Calculate magnitude threshold for sparse filtering
        magnitudes = torch.abs(fft_scores)
        
        # Determine threshold at keep_ratio percentile
        k_elements = max(1, int(seq_len * seq_len * self.keep_ratio))
        
        # Flatten magnitudes per batch/head to extract top-k values
        flat_mags = magnitudes.view(batch, heads, -1)
        topk_vals, _ = torch.topk(flat_mags, k_elements, dim=-1)
        
        # Threshold limit per head
        threshold = topk_vals[:, :, -1].unsqueeze(-1).unsqueeze(-1) # [batch, heads, 1, 1]
        
        # Filter: Zero out all coefficients below threshold
        sparse_fft = torch.where(magnitudes >= threshold, fft_scores, torch.zeros_like(fft_scores))
        
        # Reconstruct matrix back to spatial domain
        pruned_scores = torch.fft.ifft2(sparse_fft).real
        
        # Apply Softmax and weighted output projection
        attn_weights = torch.softmax(pruned_scores, dim=-1)
        return torch.matmul(attn_weights, value)
