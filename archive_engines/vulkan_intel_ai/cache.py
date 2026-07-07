import logging
import faiss
import numpy as np
from typing import Dict, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SemanticCache:
    """
    LAYER 8: SEMANTIC CACHING
    Avoids re-computing expensive LLM passes for similar queries.
    """
    def __init__(self, threshold: float = 0.92):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.cache_map: Dict[int, str] = {}
        self.threshold = threshold
        self.counter = 0

    def get(self, query: str) -> Optional[str]:
        if not self.cache_map: return None
        
        emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(emb)
        dists, indices = self.index.search(np.array(emb).astype('float32'), 1)
        
        if indices[0][0] != -1 and dists[0][0] > self.threshold:
            logger.info(f"Semantic Cache Hit (Score: {dists[0][0]:.3f})")
            return self.cache_map[indices[0][0]]
        return None

    def put(self, query: str, result: str):
        emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(emb)
        self.index.add(np.array(emb).astype('float32'))
        self.cache_map[self.counter] = result
        self.counter += 1
