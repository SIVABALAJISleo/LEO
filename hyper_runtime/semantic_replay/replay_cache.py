import numpy as np
import faiss
import json
import os
import time

class SemanticReplayCache:
    def __init__(self, embedding_dim=384, threshold=0.92, cache_dir=".hyper_cache/replay"):
        self.embedding_dim = embedding_dim
        self.threshold = threshold
        self.cache_dir = cache_dir
        self.index = faiss.IndexFlatIP(embedding_dim) # Cosine similarity if normalized
        self.responses = []
        self.hits = 0
        self.misses = 0
        os.makedirs(cache_dir, exist_ok=True)
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def add(self, embedding, response, lineage_data=None):
        emb = self._normalize(np.array(embedding, dtype=np.float32))
        self.index.add(np.expand_dims(emb, axis=0))
        self.responses.append({
            "response": response,
            "timestamp": time.time(),
            "lineage": lineage_data or {}
        })

    def search(self, embedding):
        if self.index.ntotal == 0:
            self.misses += 1
            return None, 0.0
            
        emb = self._normalize(np.array(embedding, dtype=np.float32))
        D, I = self.index.search(np.expand_dims(emb, axis=0), 1)
        score = D[0][0]
        
        if score >= self.threshold:
            self.hits += 1
            return self.responses[I[0][0]]["response"], float(score)
        
        self.misses += 1
        return None, float(score)
        
    def get_metrics(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total) if total > 0 else 0
        return {"hits": self.hits, "misses": self.misses, "hit_rate": hit_rate, "total_entries": self.index.ntotal}
