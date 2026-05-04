import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime

class SemanticCache:
    """
    LAYER 0: SEMANTIC CACHE
    Goal: Return answers instantly if similar query already exists.
    Threshold: Configurable similarity (e.g., 0.92)
    """
    def __init__(self, threshold: float = 0.92):
        self.threshold = threshold
        self.cache_db: Dict[int, Dict[str, Any]] = {} # Mock vector DB: {hash: {embedding, response}}

    def query(self, query_embedding: np.ndarray) -> Optional[str]:
        """
        Performs similarity search against cached embeddings.
        Returns the response if similarity >= threshold.
        """
        for entry in self.cache_db.values():
            # Simulated cosine similarity
            similarity = np.dot(query_embedding, entry['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(entry['embedding'])
            )
            
            if similarity >= self.threshold:
                return entry['response']
        
        return None

    def store(self, query_embedding: np.ndarray, response: str):
        """
        Stores a new query-response pair in the cache index.
        """
        entry_hash = hash(tuple(query_embedding.flatten()))
        self.cache_db[entry_hash] = {
            "embedding": query_embedding,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

# Singleton instance for the system
semantic_cache = SemanticCache()
吐
