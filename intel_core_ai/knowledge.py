import faiss
import numpy as np
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class IntelKnowledgeSystem:
    """
    LAYER 5 & 7: KNOWLEDGE SYSTEM & CACHING
    - 3-Tier Retrieval: Exact Cache -> Semantic Cache -> FAISS.
    - Tier 1: Dict Cache.
    - Tier 2: FAISS Vector Index.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # Lightweight embedding model for CPU efficiency
        self.encoder = SentenceTransformer(model_name)
        self.dim = self.encoder.get_sentence_embedding_dimension()
        
        # Layer 7: Exact Match Cache (L1)
        self.exact_cache: Dict[str, str] = {}
        
        # Layer 5: Vector DB (Tier 2)
        self.index = faiss.IndexFlatIP(self.dim)
        self.documents: List[str] = []
        
        logger.info("Intel Knowledge System Ready (FAISS + Semantic Cache).")

    def seed_knowledge(self, docs: List[str]):
        if not docs: return
        embeddings = self.encoder.encode(docs, convert_to_tensor=False)
        faiss.normalize_L2(embeddings)
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(docs)

    def retrieve(self, query: str, top_k: int = 1) -> Optional[str]:
        # 1. Exact Cache (L1)
        if query in self.exact_cache:
            return self.exact_cache[query]
            
        # 2. Vector Retrieval (Tier 2)
        query_emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_emb)
        
        distances, indices = self.index.search(np.array(query_emb).astype('float32'), top_k)
        
        if indices[0][0] != -1 and distances[0][0] > 0.7:
            result = self.documents[indices[0][0]]
            self.exact_cache[query] = result # Promote to L1
            return result
            
        return None
