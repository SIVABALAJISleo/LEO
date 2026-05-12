import redis
import faiss
import numpy as np
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class HybridCache:
    """
    Module 2: FAST PATH -> CACHE
    L1: Redis (Exact Match)
    L2: FAISS (Semantic similarity)
    """
    def __init__(self, embedding_dim: int = 384, redis_host: str = "localhost", redis_port: int = 6379):
        # L1: Redis
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=0, socket_timeout=1)
            self.redis.ping()
            self.redis_available = True
        except Exception as e:
            import os
            if not os.getenv("CI"):
                logger.warning(f"Redis not available, using local dict fallback. Error: {e}")
            self.redis_available = False
            self.redis_fallback = {}

        # L2: FAISS
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = [] # Stores query and response for L2
        self.threshold = 0.15 # L2 similarity threshold (L2 distance, so lower is closer)

    def get_l1(self, query: str) -> Optional[Dict[str, Any]]:
        """Exact match lookup."""
        if self.redis_available:
            try:
                data = self.redis.get(f"l1:{query}")
                return json.loads(data) if data else None
            except Exception:
                return None
        return self.redis_fallback.get(query)

    def get_l2(self, embedding: np.ndarray) -> Optional[Dict[str, Any]]:
        """Semantic similarity lookup."""
        if self.index.ntotal == 0:
            return None
            
        # FAISS search
        D, I = self.index.search(embedding.reshape(1, -1).astype('float32'), 1)
        
        if D[0][0] < self.threshold:
            idx = I[0][0]
            if idx < len(self.metadata):
                return self.metadata[idx]
        return None

    def set(self, query: str, response: Dict[str, Any], embedding: np.ndarray):
        """Store in both L1 and L2."""
        # Update L1
        if self.redis_available:
            try:
                self.redis.set(f"l1:{query}", json.dumps(response), ex=3600) # 1 hour cache
            except Exception:
                pass
        else:
            self.redis_fallback[query] = response
            
        # Update L2
        self.index.add(embedding.reshape(1, -1).astype('float32'))
        self.metadata.append(response)

global_hybrid_cache = HybridCache()
