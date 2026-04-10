import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = None
        if HAS_CROSS_ENCODER:
            try:
                # CPU-friendly loading
                self.model = CrossEncoder(model_name)
                logger.info(f"reranker_loaded: model={model_name}")
            except Exception as e:
                logger.warning(f"reranker_load_failed: {e}")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """Reranks documents using a cross-encoder for absolute precision."""
        if not documents:
            return []
        
        if not self.model or not HAS_CROSS_ENCODER:
            # Fallback: Sort by existing hybrid score if reranker is unavailable
            return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

        try:
            # Prepare pairs for cross-encoder
            pairs = [[query, doc["content"]] for doc in documents]
            scores = self.model.predict(pairs)
            
            # Attach new scores and sort
            for i, score in enumerate(scores):
                documents[i]["rerank_score"] = float(score)
            
            reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
            logger.debug(f"rerank_complete: count={len(documents)}")
            return reranked[:top_k]
        except Exception as e:
            logger.error(f"rerank_execution_failed: {e}")
            return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

# Global instance for easy access
global_reranker = Reranker()
