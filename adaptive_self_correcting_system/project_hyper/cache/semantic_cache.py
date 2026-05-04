import numpy as np
from typing import Optional, Dict, Any

class SemanticCache:
    """
    LAYER 3: SEMANTIC CACHE (FUZZY)
    Uses dot-product similarity (cosine proxy) to find existing answers.
    """
    def __init__(self, threshold: float = 0.92):
        self.threshold = threshold
        self.cache_db: Dict[int, Dict[str, Any]] = {} # Mock: {hash: {embedding, answer, confidence}}

    def lookup(self, query_embedding: np.ndarray) -> Optional[Dict[str, Any]]:
        # Fuzzy match logic
        for entry in self.cache_db.values():
            similarity = np.dot(query_embedding, entry['embedding'])
            if similarity >= self.threshold:
                return entry
        return None

    def insert(self, embedding: np.ndarray, prompt: str, answer: str):
        prompt_hash = hash(prompt)
        self.cache_db[prompt_hash] = {
            "embedding": embedding,
            "answer": answer,
            "confidence": 1.0,
            "timestamp": "now"
        }

semantic_cache = SemanticCache()
吐
