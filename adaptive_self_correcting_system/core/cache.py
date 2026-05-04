import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime

class SemanticCache:
    """
    LAYER 0: SEMANTIC CACHE
    Goal: Bypasses compute for similar historical queries.
    Similarity threshold (>= 0.94)
    """
    def __init__(self, threshold: float = 0.94):
        self.threshold = threshold
        # In production, this would be FAISS/Chroma
        self.vector_index: Dict[int, Dict[str, Any]] = {}

    def lookup(self, embedding: np.ndarray) -> Optional[str]:
        """
        Similarity lookup: Dot-product similarity on normalized vectors.
        """
        for entry in self.vector_index.values():
            similarity = np.dot(embedding, entry['embedding'])
            if similarity >= self.threshold:
                return entry['response']
        return None

    def commit(self, embedding: np.ndarray, response: str):
        """
        Stores result for future reuse.
        """
        entry_id = hash(tuple(embedding))
        self.vector_index[entry_id] = {
            "embedding": embedding,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

# Singleton instance
semantic_cache = SemanticCache()
吐
