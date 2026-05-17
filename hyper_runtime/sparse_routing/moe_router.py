import numpy as np

class MoERouter:
    """
    Mixture-of-Experts Router.
    Routes tokens to top-k experts based on gating network probabilities.
    """
    def __init__(self, num_experts: int = 8, top_k: int = 2, hidden_dim: int = 256):
        self.num_experts = num_experts
        self.top_k = min(top_k, num_experts)
        self.hidden_dim = hidden_dim
        
        # Mock gating weights (hidden_dim -> num_experts)
        # In a real model, these are learned parameters
        np.random.seed(42)
        self.gate_weights = np.random.randn(hidden_dim, num_experts).astype(np.float32)

    def route(self, token_embeddings: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        """
        Routes tokens to experts.
        Returns: 
        - expert_indices: [batch_size, seq_len, top_k]
        - routing_weights: [batch_size, seq_len, top_k]
        - sparsity_ratio: float
        """
        # Calculate gating logits: [batch_size, seq_len, num_experts]
        logits = np.dot(token_embeddings, self.gate_weights)
        
        # Softmax over experts
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        
        # Top-k routing
        expert_indices = np.argsort(-probs, axis=-1)[:, :, :self.top_k]
        routing_weights = np.take_along_axis(probs, expert_indices, axis=-1)
        
        # Normalize weights
        routing_weights = routing_weights / np.sum(routing_weights, axis=-1, keepdims=True)
        
        # Sparsity ratio: proportion of experts NOT activated
        sparsity_ratio = 1.0 - (self.top_k / self.num_experts)
        
        return expert_indices, routing_weights, sparsity_ratio
