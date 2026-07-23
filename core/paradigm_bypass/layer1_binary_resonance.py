import numpy as np
try:
    import pyopencl as cl
except ImportError:
    cl = None

from numba import njit, prange

class BinaryNeuralNetwork:
    def __init__(self, layer_size):
        self.layer_size = layer_size
        # Random binary weights: 0 or 1
        self.weights = np.random.randint(0, 2, (layer_size, layer_size), dtype=np.uint8)

    def binarize_weights(self):
        # Already binary in this mock
        pass

    def binarize_input(self, x):
        # x > 0 -> 1 else 0
        return (x > 0).astype(np.uint8)

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def forward_numba(x, w):
        out = np.zeros(w.shape[0], dtype=np.int32)
        for i in prange(w.shape[0]):
            count = 0
            for j in range(w.shape[1]):
                # XNOR: ~(x ^ w) & 1
                xnor = ~(x[j] ^ w[i, j]) & 1
                count += xnor
            out[i] = count
        return out

    def forward(self, x):
        x_bin = self.binarize_input(x)
        return self.forward_numba(x_bin, self.weights)

class HyperdimensionalResonanceEngine:
    def __init__(self, dim=10000):
        self.dim = dim
        self.memory = {}

    def encode_to_hd(self, data) -> np.ndarray:
        # Simple pseudo-random HD mapping based on hash
        np.random.seed(abs(hash(str(data))) % (2**32))
        return np.random.randint(0, 2, self.dim, dtype=np.uint8)

    def resonance_match(self, query: str):
        query_hd = self.encode_to_hd(query)
        best_match = None
        best_score = -1
        
        for key, hd_vec in self.memory.items():
            # Hamming distance based similarity (XNOR popcnt)
            match_score = np.sum(~(query_hd ^ hd_vec) & 1)
            if match_score > best_score:
                best_score = match_score
                best_match = key

        # If no memory, just bundle
        if best_match is None:
            self.memory[str(query)] = query_hd
            return query
            
        return best_match

    def bundle_patterns(self, patterns: list):
        if not patterns:
            return np.zeros(self.dim, dtype=np.uint8)
        # Majority rule bit voting
        sum_vec = np.sum(patterns, axis=0)
        return (sum_vec > (len(patterns) / 2)).astype(np.uint8)
