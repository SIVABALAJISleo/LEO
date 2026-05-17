class FLOPsEstimator:
    """
    Estimates theoretical FLOPs (Floating Point Operations) reduction
    achieved by HyperCore's compute-avoidance modules.
    """
    def __init__(self, hidden_dim: int = 4096, total_layers: int = 32, vocab_size: int = 32000):
        self.hidden_dim = hidden_dim
        self.total_layers = total_layers
        self.vocab_size = vocab_size
        
        # Dense FLOPs per token approx = 2 * params (ignoring attention quad term for short sequences)
        # Params approx = 12 * h^2 * layers
        self.params_per_layer = 12 * (hidden_dim ** 2)
        self.dense_flops_per_token = 2 * self.params_per_layer * total_layers

    def calculate_savings(self, 
                          is_replay_hit: bool, 
                          tome_sparsity: float, 
                          gating_sparsity: float, 
                          moe_sparsity: float, 
                          exit_layer: int) -> dict:
        """
        Calculates FLOP savings for a single forward pass.
        Returns detailed breakdown.
        """
        if is_replay_hit:
            return {
                "dense_flops": self.dense_flops_per_token,
                "actual_flops": 0.0,
                "savings_ratio": 1.0,
                "reason": "Semantic Replay"
            }
            
        # If not replayed, calculate sparse FLOPs layer by layer
        actual_flops = 0.0
        
        # We only compute up to exit_layer
        for layer in range(exit_layer):
            # Attention FLOPs (approx 4 * h^2) - reduced by Token Merging
            attn_flops = (4 * (self.hidden_dim ** 2)) * (1.0 - tome_sparsity)
            
            # FFN FLOPs (approx 8 * h^2) - reduced by Entropy Gating and MoE
            ffn_flops = (8 * (self.hidden_dim ** 2)) * (1.0 - gating_sparsity) * (1.0 - moe_sparsity)
            
            actual_flops += 2 * (attn_flops + ffn_flops)
            
        savings = 1.0 - (actual_flops / self.dense_flops_per_token)
        
        return {
            "dense_flops": self.dense_flops_per_token,
            "actual_flops": actual_flops,
            "savings_ratio": savings,
            "reason": "Sparse Execution"
        }
