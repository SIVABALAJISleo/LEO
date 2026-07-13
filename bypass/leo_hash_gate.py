import numpy as np
import logging

logger = logging.getLogger(__name__)

class HashGate:
    """
    Layer 1: The Hash-Gate (O(1) Inference)
    Replaces math with memory using Locality Sensitive Hashing (Random Hyperplanes).
    """
    def __init__(self, input_dim=256, hash_size=64):
        self.input_dim = input_dim
        self.hash_size = hash_size
        
        # Random hyperplanes for LSH projection
        # Seeded for consistency across runs
        np.random.seed(42)
        self.hyperplanes = np.random.randn(self.hash_size, self.input_dim)
        
        # O(1) Cache Storage
        # key: 64-bit integer hash -> value: cached output tensor
        self.cache = {}
        
    def _compute_lsh(self, input_tensor: np.ndarray) -> int:
        """
        Projects input through hyperplanes and creates a 64-bit binary hash.
        """
        # Slice a tiny contiguous chunk before flattening to avoid massive memory copies
        flat_input = input_tensor[:2, :128, :1].flatten()[:self.input_dim]
        if len(flat_input) < self.input_dim:
            flat_input = np.pad(flat_input, (0, self.input_dim - len(flat_input)))
            
        projections = np.dot(self.hyperplanes, flat_input)
        bits = (projections > 0).astype(int)
        
        # Convert binary array to 64-bit integer hash
        hash_val = 0
        for bit in bits:
            hash_val = (hash_val << 1) | bit
        return hash_val

    def hamming_distance(self, hash1: int, hash2: int) -> int:
        """Calculates exact bit difference."""
        x = hash1 ^ hash2
        return bin(x).count('1')

    def check_cache(self, input_tensor: np.ndarray, similarity_threshold=0.98):
        """
        Hashes the input and does a rapid dictionary lookup.
        If a similar hash exists, return the cached result instantly.
        """
        current_hash = self._compute_lsh(input_tensor)
        
        # Exact match (O(1))
        if current_hash in self.cache:
            logger.debug("[HashGate] EXACT MATCH FOUND. Bypassing Model.")
            return True, self.cache[current_hash]
            
        # Approximate match (Simulated for speed)
        # In a true massive database, we'd use a VPTree or Faiss.
        # Here we do a fast scan of recent keys.
        max_dist = int(self.hash_size * (1.0 - similarity_threshold))
        
        for cached_hash, output in self.cache.items():
            dist = self.hamming_distance(current_hash, cached_hash)
            if dist <= max_dist:
                logger.debug(f"[HashGate] LSH MATCH (>98%). Distance: {dist}. Bypassing Model.")
                return True, output
                
        return False, current_hash

    def store(self, hash_val: int, output_result):
        """Stores the neural network output linked to the input hash."""
        self.cache[hash_val] = output_result
        if len(self.cache) > 100000:
            # Prevent RAM overflow by clearing older entries randomly or via LRU
            keys_to_delete = list(self.cache.keys())[:1000]
            for k in keys_to_delete:
                del self.cache[k]
