import numpy as np

class SimplifiedMambaBlock:
    """
    Simulates a linear-time sequence modeling block (Mamba / State Space Model).
    Avoids O(N^2) attention bottlenecks via recurrent state updates.
    """
    def __init__(self, d_model=256, d_state=16):
        self.d_model = d_model
        self.d_state = d_state
        self.A = np.random.randn(d_model, d_state) * 0.1
        self.B = np.random.randn(d_model, d_state) * 0.1
        self.C = np.random.randn(d_model, d_state) * 0.1
        
    def forward_streaming(self, x_seq, initial_state=None):
        """
        x_seq: [seq_len, d_model]
        Linear time complexity: O(seq_len * d_model * d_state)
        """
        seq_len = x_seq.shape[0]
        state = initial_state if initial_state is not None else np.zeros((self.d_model, self.d_state))
        outputs = []
        
        for t in range(seq_len):
            state = self.A * state + self.B * x_seq[t:t+1].T
            y_t = np.sum(self.C * state, axis=1)
            outputs.append(y_t)
            
        return np.array(outputs), state
