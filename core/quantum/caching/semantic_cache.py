"""
LEO Semantic Cache Flat Index Wrapper
"""
import numpy as np
import faiss
from typing import Optional, Tuple

class SemanticCache:
    """
    Semantic search cache provider built on FAISS Flat L2 or Inner Product indices.
    """
    
    def __init__(self, dimension: int = 384, threshold: float = 0.85):
        self.dimension = dimension
        self.threshold = threshold
        # Inner Product Flat Index (requires normalized vectors for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)
        self.queries = []
        self.responses = []
        
    def add(self, vector: np.ndarray, query: str, response: str):
        """Add embedding vector to the FAISS index with metadata mapping"""
        vector = vector.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        self.index.add(vector)
        self.queries.append(query)
        self.responses.append(response)
        
    def query_similarity(self, vector: np.ndarray) -> Tuple[Optional[str], float]:
        """Queries the index and returns the closest match if similarity threshold is met"""
        if self.index.ntotal == 0:
            return None, 0.0
            
        vector = vector.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        distances, indices = self.index.search(vector, 1)
        if len(indices) > 0 and indices[0][0] >= 0:
            idx = indices[0][0]
            similarity = float(distances[0][0])
            if similarity >= self.threshold:
                return self.responses[idx], similarity
                
        return None, 0.0
