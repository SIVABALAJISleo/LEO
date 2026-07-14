"""
phoenix/hierarchical_rag.py
Hierarchical RAG Pipeline.
Chunk -> Embed (tiny model) -> FAISS Index (sub-ms retrieval) -> Inject.
"""

import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

class HierarchicalRAGEngine:
    """
    RAG Engine using FAISS for ultra-fast embedding similarity search.
    Documents are chunked, embedded, and injected into the ContextManager.
    """
    def __init__(self, embedding_dim: int = 384):
        self.dim = embedding_dim
        self.index = None
        self.doc_map: Dict[int, str] = {}
        
        try:
            import faiss
            # Inner Product (Cosine similarity if normalized)
            self.index = faiss.IndexFlatIP(self.dim)
            logger.info(f"[RAG] FAISS Index initialized with dim {self.dim}")
        except ImportError:
            logger.warning("[RAG] faiss not installed. RAG Engine disabled.")

    def _dummy_embed(self, text: str) -> np.ndarray:
        """Simulate an embedding model (e.g., bge-small-en-v1.5)."""
        # In production, use sentence-transformers here
        np.random.seed(len(text))
        vec = np.random.randn(self.dim).astype(np.float32)
        return vec / np.linalg.norm(vec)

    def add_document(self, text: str):
        if self.index is None: return
        
        # Simple chunking (e.g., 512 tokens)
        words = text.split()
        chunk_size = 200 # approx 250 tokens
        
        import faiss
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            vec = self._dummy_embed(chunk)
            
            idx = len(self.doc_map)
            self.doc_map[idx] = chunk
            self.index.add(np.expand_dims(vec, axis=0))

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        if self.index is None or len(self.doc_map) == 0:
            return []
            
        q_vec = self._dummy_embed(query)
        distances, indices = self.index.search(np.expand_dims(q_vec, axis=0), top_k)
        
        results = []
        for idx in indices[0]:
            if idx in self.doc_map:
                results.append(self.doc_map[idx])
                
        return results
