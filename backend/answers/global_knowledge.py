"""
Global Knowledge Layer (PHASE 3)
Stores cross-tenant shared intelligence for common domain facts.
"""
import logging
import faiss
import numpy as np
import os
from typing import Optional, List, Dict, Any
from backend.ingest.embedding_pipeline import global_embedding_pipeline

logger = logging.getLogger(__name__)

# Constants
KNOWLEDGE_PATH = os.path.join(os.getcwd(), "data", "global_knowledge.idx")
DIMENSION = 384
THRESHOLD = 0.94  # Very high threshold for global facts

class GlobalKnowledgeLayer:
    """
    Shared semantic index for universal facts.
    """
    def __init__(self):
        self._index = faiss.IndexFlatL2(DIMENSION)
        self._facts: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        # In a production system, this would load from a shared SQLDB
        # For HYPER, we use a local FAISS index for speed.
        if os.path.exists(KNOWLEDGE_PATH):
            try:
                self._index = faiss.read_index(KNOWLEDGE_PATH)
                logger.info("global_knowledge_index_loaded")
            except Exception as e:
                logger.error(f"global_knowledge_load_failed: {e}")

    def lookup(self, query: str) -> Optional[str]:
        """Looks up shared knowledge for a query."""
        if self._index.ntotal == 0:
            return None
            
        emb = global_embedding_pipeline.get_embeddings([query])[0].astype(np.float32)
        dist, indices = self._index.search(np.array([emb]), k=1) # type: ignore
        
        if indices[0][0] != -1:
            similarity = 1.0 - (dist[0][0] / 2.0)
            if similarity >= THRESHOLD:
                # In this demo, we store facts in a local list mapping to indices
                return self._facts[indices[0][0]]["answer"]
        return None

    def add_fact(self, query: str, answer: str):
        """Adds a fact to the shared cross-tenant layer."""
        emb = global_embedding_pipeline.get_embeddings([query])[0].astype(np.float32)
        self._index.add(np.array([emb])) # type: ignore
        self._facts.append({"query": query, "answer": answer})
        logger.info(f"global_fact_added: query_len={len(query)}")

global_knowledge = GlobalKnowledgeLayer()
