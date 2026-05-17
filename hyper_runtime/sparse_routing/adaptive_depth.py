import numpy as np

class AdaptiveDepthController:
    """
    Early Exit / Layer Skipping mechanism.
    Evaluates confidence at intermediate layers and skips remaining layers if confidence is high.
    """
    def __init__(self, total_layers: int = 12, exit_threshold: float = 0.85):
        self.total_layers = total_layers
        self.exit_threshold = exit_threshold
        
    def evaluate_early_exit(self, layer_idx: int, hidden_states: np.ndarray) -> tuple[bool, float]:
        """
        Simulates evaluating the entropy/confidence of hidden states to decide early exit.
        Returns: (should_exit, confidence_score)
        """
        # In a real model, this might involve a small classifier or entropy over softmax logits
        # Here we simulate confidence based on L2 norm variance across batch
        norm = np.linalg.norm(hidden_states, axis=-1)
        variance = np.var(norm)
        
        # Simulated confidence score that tends to increase with depth
        base_confidence = min(1.0, layer_idx / (self.total_layers * 0.8))
        confidence = base_confidence + (np.clip(variance, 0.0, 1.0) * 0.2)
        
        should_exit = confidence >= self.exit_threshold
        return should_exit, float(confidence)
        
    def calculate_compute_savings(self, exit_layer: int) -> float:
        """Returns the percentage of layers skipped."""
        return max(0.0, (self.total_layers - exit_layer) / self.total_layers)
