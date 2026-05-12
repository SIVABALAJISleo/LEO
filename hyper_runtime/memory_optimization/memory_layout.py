import numpy as np

class StructureOfArrays:
    """
    Implements Memory + Data Movement Optimization (Section 21).
    Structure-of-Arrays (SoA) layout instead of Array-of-Structures (AoS)
    to maximize SIMD auto-vectorization and cache locality.
    """
    def __init__(self, size):
        self.size = size
        self.q_vectors = np.zeros((size, 128), dtype=np.float32)
        self.k_vectors = np.zeros((size, 128), dtype=np.float32)
        self.v_vectors = np.zeros((size, 128), dtype=np.float32)
        
    def batch_compute_attention(self, active_indices):
        """
        Vectorized attention computation over active elements.
        Because data is stored in SoA format, CPU cache-lines are perfectly utilized.
        """
        active_q = self.q_vectors[active_indices]
        active_k = self.k_vectors[active_indices]
        
        scores = np.dot(active_q, active_k.T)
        return scores
