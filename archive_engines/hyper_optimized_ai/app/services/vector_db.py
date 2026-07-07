import faiss
import os
import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from archive_engines.hyper_optimized_ai.config import settings

logger = logging.getLogger(__name__)

class CacheResult(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any] = {}

class VectorDBService:
    """
    Service for FAISS-based semantic search and caching.
    Uses sentence-transformers for local CPU-optimized embeddings.
    """
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = index_path
        self.metadata_path = metadata_path
        # Use a very small, fast model for CPU optimization
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device='cpu')
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._init_empty_index()
        else:
            self._init_empty_index()

    def _init_empty_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info("Initialized empty FAISS index.")

    async def search_cache(self, text: str, threshold: float = 0.92) -> Optional[CacheResult]:
        if self.index.ntotal == 0:
            return None

        # 1. Generate embedding
        embedding = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(embedding)

        # 2. Search FAISS
        scores, indices = self.index.search(embedding, k=1)
        
        if indices[0][0] != -1:
            score = float(scores[0][0])
            if score >= threshold:
                meta = self.metadata[indices[0][0]]
                return CacheResult(
                    content=meta["response"], 
                    score=score,
                    metadata=meta.get("extra", {})
                )
        
        return None

    async def add_to_cache(self, query: str, response: str, extra: Dict[str, Any] = None):
        embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        
        self.index.add(embedding)
        self.metadata.append({
            "query": query,
            "response": response,
            "extra": extra or {}
        })
        
        self._save()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    async def rag_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # This would typically be a separate index for knowledge, but for this demo
        # we'll use a mock internal knowledge base
        knowledge_base = [
            {"text": "NVIDIA H100 GPUs provide superior FP8 performance for AI training.", "source": "tech_docs", "recency": 0.9},
            {"text": "Local CPU inference is best served via GGUF quantization (Q4_K_M).", "source": "benchmarks", "recency": 0.95},
            {"text": "FastAPI async endpoints reduce overhead in high-concurrency systems.", "source": "api_standards", "recency": 0.8}
        ]
        
        # Simple keyword match for demo
        results = [k for k in knowledge_base if any(word in k["text"].lower() for word in query.lower().split())]
        return results[:top_k]

    async def invalidate_cache(self, query: str):
        # In a real system, we'd remove or re-index. 
        # For this demo, we'll just clear the index if it gets too large or corrupted
        pass
