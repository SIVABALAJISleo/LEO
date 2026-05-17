class RecomputationEngine:
    """
    Simulates activation checkpointing (recomputation).
    Instead of storing the intermediate states, we only store the input and recompute
    the intermediate states when needed (e.g., for backward pass or verification).
    """
    def __init__(self):
        self.checkpoints = {} # id -> (input_tensor, metadata)
        
    def checkpoint(self, cp_id: str, input_tensor, metadata=None):
        """Saves the input required to recompute the block later."""
        # In reality, we'd store a view or a compressed version
        self.checkpoints[cp_id] = (input_tensor, metadata)
        
    def recompute(self, cp_id: str, forward_fn) -> tuple:
        """
        Re-runs the forward function from the saved checkpoint to 
        regenerate the discarded activations.
        """
        if cp_id not in self.checkpoints:
            raise KeyError("Checkpoint not found.")
            
        input_tensor, metadata = self.checkpoints[cp_id]
        
        # Regenerate the activations
        regenerated_activations = forward_fn(input_tensor)
        return regenerated_activations
