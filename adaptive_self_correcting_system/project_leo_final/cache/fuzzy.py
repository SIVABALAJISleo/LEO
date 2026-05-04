import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SemanticCache:
    """
    LAYER 3: SEMANTIC CACHE (FUZZY + LRU)
    Threshold: 0.92
    """
    def __init__(self, threshold: float = 0.92, ttl_hours: int = 24):
        self.threshold = threshold
        self.ttl = ttl_hours
        self.db: Dict[int, Dict[str, Any]] = {} # {hash: {embedding, query, response, confidence, expiry}}

    def lookup(self, embedding: np.ndarray) -> Optional[Dict[str, Any]]:
        now = datetime.now()
        for h, entry in list(self.db.items()):
            # TTL Check
            if now > entry['expiry']:
                del self.db[h]
                continue
            
            # Fuzzy match (cosine similarity proxy)
            similarity = np.dot(embedding, entry['embedding'])
            if similarity >= self.threshold:
                # Frequency Boost logic would go here
                return entry
        return None

    def store(self, embedding: np.ndarray, query: str, response: str):
        h = hash(query)
        self.db[h] = {
            "embedding": embedding,
            "query": query,
            "response": response,
            "confidence": 1.0,
            "expiry": datetime.now() + timedelta(hours=self.ttl)
        }

fuzzy_cache = SemanticCache()
吐
