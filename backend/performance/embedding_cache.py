import numpy as np
import hashlib
from typing import Optional, Dict

class EmbeddingCache:
    """
    LRU-style cache for query embeddings to avoid redundant GPU/CPU encoding calls.
    Addresses the 'Last-Mile Compute' performance bottleneck.
    """
    def __init__(self, max_size: int = 2000):
        self.cache: Dict[str, np.ndarray] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, query: str) -> Optional[np.ndarray]:
        """Retrieves cached embedding using a SHA-256 hash of the normalized query."""
        q_hash = self._hash(query)
        if q_hash in self.cache:
            self.hits += 1
            return self.cache[q_hash]
        self.misses += 1
        return None

    def set(self, query: str, embedding: np.ndarray):
        """Stores embedding in the cache, enforcing capacity limits."""
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction for speed
            first_key = next(iter(self.cache))
            self.cache.pop(first_key)
        
        q_hash = self._hash(query)
        self.cache[q_hash] = embedding

    def _hash(self, query: str) -> str:
        return hashlib.sha256(query.lower().strip().encode()).hexdigest()

    def stats(self) -> dict:
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": float(f"{ratio:.2f}"),
            "cache_size": len(self.cache)
        }

global_embedding_cache = EmbeddingCache()
