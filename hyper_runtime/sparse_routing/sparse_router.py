import numpy as np

class SparseExpertRouter:
    def __init__(self, num_experts=8, top_k=2):
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate_weights = np.random.randn(4096, num_experts)
        
    def route(self, hidden_states):
        logits = np.dot(hidden_states, self.gate_weights) 
        weights = np.exp(logits) / np.sum(np.exp(logits), axis=-1, keepdims=True)
        top_indices = np.argsort(logits, axis=-1)[:, -self.top_k:]
        return top_indices, weights
