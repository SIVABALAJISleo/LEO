import faiss
import numpy as np
import os
import json
import logging
from typing import List, Optional, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class UnifiedVectorDB:
    """
    Shared FAISS service for semantic caching and RAG.
    """
    def __init__(self, index_path: str, metadata_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = SentenceTransformer(model_name, device='cpu')
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    async def search(self, text: str, threshold: float = 0.92) -> Optional[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return None

        embedding = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        scores, indices = self.index.search(embedding, k=1)
        
        if indices[0][0] != -1:
            score = float(scores[0][0])
            if score >= threshold:
                return self.metadata[indices[0][0]]
        return None

    async def store(self, query: str, response: str, metadata: Dict[str, Any] = None):
        embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        self.index.add(embedding)
        self.metadata.append({
            "query": query,
            "response": response,
            "extra": metadata or {}
        })
        self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)
            
    async def invalidate(self, query: str):
        # Mark as invalid or rebuild
        pass
