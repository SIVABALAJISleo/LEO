import time
import logging
import numpy as np
import hashlib
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class MultiLevelSemanticCache:
    """
    Subsystem 4: Multi-Level Semantic Cache.
    Avoids LLM inference entirely by checking for exact string matches
    or dense vector semantic similarity to previous queries.
    Hierarchical Eviction manages RAM usage.
    """
    def __init__(self, max_exact_items: int = 10000, max_semantic_items: int = 5000):
        # Level 1: Exact Match (Hash-based, O(1) latency)
        self.exact_cache: Dict[str, Tuple[str, float]] = {}
        self.max_exact_items = max_exact_items
        
        # Level 2: Semantic Match (Vector-based similarity)
        self.semantic_cache_queries = []
        self.semantic_cache_vectors = []
        self.semantic_cache_responses = []
        self.semantic_cache_timestamps = []
        self.max_semantic_items = max_semantic_items

    def _hash_query(self, query: str) -> str:
        """Normalized string hash for L1 cache."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def check_cache(self, query: str, query_vector: Optional[np.ndarray] = None, similarity_threshold: float = 0.95) -> Optional[str]:
        """Checks Level 1 then Level 2 for a cached response."""
        # Check Level 1 (Exact Match)
        q_hash = self._hash_query(query)
        if q_hash in self.exact_cache:
            response, _ = self.exact_cache[q_hash]
            # Update access time for LRU
            self.exact_cache[q_hash] = (response, time.time())
            logger.info("L1 Semantic Cache HIT (Exact Match). Inference Avoided.")
            return response
            
        # Check Level 2 (Semantic Match)
        if query_vector is not None and len(self.semantic_cache_vectors) > 0:
            # Cosine similarity against all cached vectors
            cache_matrix = np.vstack(self.semantic_cache_vectors)
            dot_products = np.dot(cache_matrix, query_vector)
            norms = np.linalg.norm(cache_matrix, axis=1) * np.linalg.norm(query_vector)
            similarities = dot_products / (norms + 1e-9)
            
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score >= similarity_threshold:
                logger.info(f"L2 Semantic Cache HIT (Similarity: {best_score:.3f}). Inference Avoided.")
                self.semantic_cache_timestamps[best_idx] = time.time()
                return self.semantic_cache_responses[best_idx]
                
        return None

    def add_to_cache(self, query: str, response: str, query_vector: Optional[np.ndarray] = None):
        """Adds a new query/response pair to the cache, evicting old items if necessary."""
        current_time = time.time()
        
        # Add to L1
        if len(self.exact_cache) >= self.max_exact_items:
            # LRU Eviction
            oldest_key = min(self.exact_cache.keys(), key=lambda k: self.exact_cache[k][1])
            del self.exact_cache[oldest_key]
        self.exact_cache[self._hash_query(query)] = (response, current_time)
        
        # Add to L2
        if query_vector is not None:
            if len(self.semantic_cache_vectors) >= self.max_semantic_items:
                # Evict oldest
                oldest_idx = np.argmin(self.semantic_cache_timestamps)
                self.semantic_cache_queries.pop(oldest_idx)
                self.semantic_cache_vectors.pop(oldest_idx)
                self.semantic_cache_responses.pop(oldest_idx)
                self.semantic_cache_timestamps.pop(oldest_idx)
                
            self.semantic_cache_queries.append(query)
            self.semantic_cache_vectors.append(query_vector)
            self.semantic_cache_responses.append(response)
            self.semantic_cache_timestamps.append(current_time)
