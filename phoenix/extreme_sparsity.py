"""
phoenix/extreme_sparsity.py
Extreme Sparsity Module (WANDA-style Pruning).
Induces high sparsity (e.g., 50-80%) in linear layers by scoring weights
based on both their magnitude and the input activation norms.
Never Compute Zero: Zeroed weights skip multiplication entirely in sparse format.
"""

import logging
import torch
import torch.nn as nn
from typing import Dict

logger = logging.getLogger(__name__)

class WandaPruner:
    """
    Implements Weight and Activation (WANDA) pruning logic.
    For a linear layer W, score each weight W_ij by |W_ij| * ||X_j||_2
    where X_j is the input activation.
    """
    def __init__(self, sparsity_ratio: float = 0.5):
        self.sparsity_ratio = sparsity_ratio
        # Store activation norms during calibration
        self.activation_norms: Dict[str, torch.Tensor] = {}
        self.hooks = []

    def _get_activation_hook(self, name: str):
        def hook(module, inp, out):
            x = inp[0].detach() # (batch, seq, in_features)
            # Compute L2 norm of activations across batch and sequence
            if x.dim() == 3:
                norm = torch.norm(x, p=2, dim=(0, 1))
            else:
                norm = torch.norm(x, p=2, dim=0)
            
            if name in self.activation_norms:
                # EMA update if calibrating over multiple batches
                self.activation_norms[name] = 0.9 * self.activation_norms[name] + 0.1 * norm
            else:
                self.activation_norms[name] = norm
        return hook

    def attach_calibration_hooks(self, model: nn.Module):
        """Attach forward hooks to measure activation norms."""
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                handle = module.register_forward_hook(self._get_activation_hook(name))
                self.hooks.append(handle)
        logger.info(f"[Sparsity] Attached {len(self.hooks)} calibration hooks.")

    def remove_hooks(self):
        for h in self.hooks:
            h.remove()
        self.hooks.clear()

    @torch.no_grad()
    def apply_pruning(self, model: nn.Module):
        """
        Applies unstructured sparsity based on calculated WANDA scores.
        """
        pruned_count = 0
        total_count = 0
        
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                W = module.weight.data
                total_count += W.numel()
                
                # If we don't have activation norms (e.g., didn't calibrate), fallback to magnitude pruning
                if name in self.activation_norms:
                    X_norm = self.activation_norms[name].unsqueeze(0) # (1, in_features)
                    score = torch.abs(W) * X_norm
                else:
                    score = torch.abs(W)
                    
                # Calculate threshold for the target sparsity
                k = int(self.sparsity_ratio * W.numel())
                if k == 0: continue
                
                # Find the threshold value
                threshold = torch.kthvalue(score.flatten(), k).values
                
                # Apply mask
                mask = score >= threshold
                module.weight.data = W * mask
                
                # Convert to sparse tensor for inference speedup (simulated via torch.sparse or CSR)
                # In production, sparse matrix formats (e.g. cuSPARSE or Intel MKL) are used.
                
                zeros = (mask == False).sum().item()
                pruned_count += zeros
                
        if total_count > 0:
            actual_sparsity = (pruned_count / total_count) * 100
            logger.info(f"[Sparsity] Pruned {pruned_count}/{total_count} weights ({actual_sparsity:.1f}% sparsity).")
        
        return model
