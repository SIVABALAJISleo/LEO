import numpy as np

class EntropyGating:
    """
    Decides whether to execute full FFN / Attention blocks based on token entropy.
    Low-entropy (highly predictable) tokens bypass dense compute.
    """
    def __init__(self, entropy_threshold: float = 0.5):
        self.entropy_threshold = entropy_threshold
        
    def estimate_token_entropy(self, hidden_states: np.ndarray) -> np.ndarray:
        """
        Estimates entropy per token.
        hidden_states: [batch_size, seq_len, hidden_dim]
        Returns: entropy_scores [batch_size, seq_len]
        """
        # In a real system, this could be the entropy of the attention distribution 
        # or predicted directly by a small routing linear layer.
        # Here we mock it based on L2 norm variance across features.
        var = np.var(hidden_states, axis=-1)
        # Normalize roughly to [0, 1]
        var_norm = var / (np.max(var) + 1e-9)
        # Higher variance implies higher information content (entropy)
        entropy_scores = np.clip(var_norm, 0.0, 1.0)
        return entropy_scores

    def apply_gating(self, hidden_states: np.ndarray) -> tuple[np.ndarray, float]:
        """
        Returns mask of active tokens and the percentage of compute skipped.
        active_mask: boolean array [batch_size, seq_len]
        """
        entropy_scores = self.estimate_token_entropy(hidden_states)
        active_mask = entropy_scores > self.entropy_threshold
        
        # Calculate sparsity ratio (percentage of tokens skipped)
        total_tokens = active_mask.size
        skipped_tokens = total_tokens - np.sum(active_mask)
        sparsity_ratio = float(skipped_tokens / total_tokens) if total_tokens > 0 else 0.0
        
        return active_mask, sparsity_ratio
