import numpy as np
import logging
from typing import Dict, Any

from .moe_router import MoERouter
from .adaptive_depth import AdaptiveDepthController
from .token_merging import TokenMerger
from .entropy_gating import EntropyGating

logger = logging.getLogger("HyperCore.SparseRouter")

class SparseIntelligenceRouter:
    """
    HyperCore MODULE 4 — Sparse Intelligence Router
    
    Activates minimum necessary compute pathways using:
    1. Token Merging (ToMe)
    2. Entropy Gating (Selective FFN execution)
    3. Mixture-of-Experts (MoE) Routing
    4. Adaptive Depth (Early Exit)
    """
    def __init__(self, hidden_dim: int = 256, total_layers: int = 12):
        self.hidden_dim = hidden_dim
        self.total_layers = total_layers
        
        self.token_merger = TokenMerger(merge_ratio=0.2)
        self.entropy_gating = EntropyGating(entropy_threshold=0.4)
        self.moe_router = MoERouter(num_experts=8, top_k=2, hidden_dim=hidden_dim)
        self.adaptive_depth = AdaptiveDepthController(total_layers=total_layers, exit_threshold=0.85)
        
        logger.info("SparseIntelligenceRouter initialized with ToMe, EntropyGating, MoE, and AdaptiveDepth.")

    def route_execution(self, hidden_states: np.ndarray) -> Dict[str, Any]:
        """
        Simulates the forward pass through the sparse routing mechanisms.
        hidden_states shape: [batch_size, seq_len, hidden_dim]
        Returns detailed telemetry on compute savings.
        """
        batch_size, seq_len, _ = hidden_states.shape
        metrics = {
            "original_tokens": int(batch_size * seq_len),
            "merged_tokens": 0,
            "tome_sparsity": 0.0,
            "gating_sparsity": 0.0,
            "moe_sparsity": 0.0,
            "depth_sparsity": 0.0,
            "exit_layer": self.total_layers,
            "total_compute_avoided_ratio": 0.0
        }
        
        # 1. Token Merging (ToMe)
        merged_states, tome_sparsity = self.token_merger.merge_tokens(hidden_states)
        metrics["merged_tokens"] = int(merged_states.shape[0] * merged_states.shape[1])
        metrics["tome_sparsity"] = round(tome_sparsity, 4)
        
        # We process layers iteratively
        current_states = merged_states
        accumulated_gating_sparsity = 0.0
        
        for layer_idx in range(self.total_layers):
            # 2. Entropy Gating (Skip FFN for predictable tokens)
            active_mask, gating_sparsity = self.entropy_gating.apply_gating(current_states)
            accumulated_gating_sparsity += gating_sparsity
            
            # 3. MoE Routing (Only active tokens go to experts)
            # In a real model, we gather active tokens, route to experts, compute, scatter back.
            # Here we just calculate the sparsity
            _, _, moe_sparsity = self.moe_router.route(current_states)
            
            # 4. Adaptive Depth (Check if we can exit early)
            should_exit, confidence = self.adaptive_depth.evaluate_early_exit(layer_idx, current_states)
            
            if should_exit:
                metrics["exit_layer"] = layer_idx + 1
                metrics["depth_sparsity"] = self.adaptive_depth.calculate_compute_savings(layer_idx + 1)
                break
                
            # Simulate state evolution (mock)
            current_states = current_states + np.random.randn(*current_states.shape).astype(np.float32) * 0.1
            
        metrics["gating_sparsity"] = round(accumulated_gating_sparsity / metrics["exit_layer"], 4)
        metrics["moe_sparsity"] = round(moe_sparsity, 4)
        
        # Calculate compounded compute reduction
        # Compute retained = (1 - ToMe) * (1 - Gating) * (1 - MoE) * (1 - Depth)
        retained = (1.0 - metrics["tome_sparsity"]) * \
                   (1.0 - metrics["gating_sparsity"]) * \
                   (1.0 - metrics["moe_sparsity"]) * \
                   (1.0 - metrics["depth_sparsity"])
                   
        metrics["total_compute_avoided_ratio"] = round(1.0 - retained, 4)
        
        return metrics
