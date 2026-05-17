import numpy as np

class SSMState:
    """
    Manages the recurrent hidden state for State Space Models (like Mamba).
    Unlike Transformers which require storing all previous tokens (O(N) memory),
    SSMs maintain a constant-size hidden state (O(1) memory) per sequence.
    """
    def __init__(self, batch_size: int, hidden_dim: int, state_dim: int):
        self.batch_size = batch_size
        self.hidden_dim = hidden_dim
        self.state_dim = state_dim
        
        # The hidden state h_t: [batch_size, hidden_dim, state_dim]
        self.h = np.zeros((batch_size, hidden_dim, state_dim), dtype=np.float32)
        
    def get_state(self) -> np.ndarray:
        return self.h
        
    def update_state(self, new_h: np.ndarray):
        """Updates the recurrent state in place."""
        self.h = new_h
        
    def get_memory_footprint_mb(self) -> float:
        return self.h.nbytes / (1024 * 1024)
