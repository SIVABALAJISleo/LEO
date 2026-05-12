import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class CacheFirstLayer:
    """LAYER 0 — CACHE FIRST"""
    def __init__(self, threshold=0.92):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.threshold = threshold
        self.store = []
        
    def _embed(self, text: str) -> np.ndarray:
        vec = self.encoder.encode([text])[0].astype('float32')
        faiss.normalize_L2(vec.reshape(1, -1))
        return vec.reshape(1, -1)

    def check_cache(self, query: str):
        if self.index.ntotal == 0:
            return None
        vec = self._embed(query)
        D, I = self.index.search(vec, 1)
        if D[0][0] >= self.threshold:
            return self.store[I[0][0]]
        return None

    def add_to_cache(self, query: str, response: str):
        vec = self._embed(query)
        self.index.add(vec)
        self.store.append(response)
