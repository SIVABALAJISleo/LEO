import faiss
import numpy as np
import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SemanticCache:
    """
    Vector-based cache to avoid redundant computation for 
    semantically similar inputs.
    """
    def __init__(self, dimension=384, cache_path='cache/semantic_cache.faiss'):
        self.dimension = dimension
        self.cache_path = cache_path
        self.metadata_path = cache_path.replace('.faiss', '.json')
        
        # Ensure cache dir exists
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        # L2 Distance Index
        self.index = faiss.IndexFlatL2(dimension)
        self.results = [] # Stores the actual result objects
        
        if os.path.exists(self.cache_path):
            self.load()

    def load(self):
        try:
            self.index = faiss.read_index(self.cache_path)
            with open(self.metadata_path, 'r') as f:
                self.results = json.load(f)
            logger.info(f"Loaded semantic cache with {len(self.results)} entries.")
        except Exception as e:
            logger.error(f"Failed to load semantic cache: {e}")

    def save(self):
        faiss.write_index(self.index, self.cache_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.results, f)

    def lookup(self, embedding: np.ndarray, threshold: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Finds the closest match in the cache.
        """
        if self.index.ntotal == 0:
            return None
            
        emb = np.array([embedding]).astype('float32')
        distances, indices = self.index.search(emb, 1)
        
        if indices[0][0] != -1 and distances[0][0] < threshold:
            logger.info(f"Semantic Cache Hit! Distance: {distances[0][0]:.4f}")
            return self.results[indices[0][0]]
            
        return None

    def store(self, embedding: np.ndarray, result: Dict[str, Any]):
        """
        Adds a new result to the cache.
        """
        emb = np.array([embedding]).astype('float32')
        self.index.add(emb)
        self.results.append(result)
        self.save()
        logger.info("Stored new result in semantic cache.")

if __name__ == "__main__":
    # Mock usage
    cache = SemanticCache()
    dummy_emb = np.random.random(384).astype('float32')
    cache.store(dummy_emb, {"output": "cached response"})
    print(f"Lookup: {cache.lookup(dummy_emb)}")
