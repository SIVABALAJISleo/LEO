import numpy as np

class MixtureOfDepthsRuntime:
    def __init__(self, capacity_factor=0.125):
        self.capacity_factor = capacity_factor
        self.router_weights = np.random.randn(4096, 1)
        
    def forward(self, hidden_states, layer_id):
        seq_len = hidden_states.shape[0]
        capacity = max(1, int(seq_len * self.capacity_factor))
        
        scores = np.dot(hidden_states, self.router_weights).squeeze()
        participating_indices = np.argsort(scores)[-capacity:]
        
        return participating_indices, capacity

    def analyze_compute_reduction(self, seq_len):
        capacity = int(seq_len * self.capacity_factor)
        skipped = seq_len - capacity
        return skipped / seq_len
