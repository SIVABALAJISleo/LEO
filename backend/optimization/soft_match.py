"""
backend/optimization/soft_match.py
Soft Match Engine for Zero Runtime Compute.

Allows reuse of answers for queries with similarity >= 0.75.
"""
import logging
from typing import Optional, Dict, Any
from backend.rag.embedding_model import search as rag_search
from backend.intelligence.delta_engine import global_delta_engine_v2

logger = logging.getLogger(__name__)

class SoftMatchEngine:
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold

    def find_match(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Looks for a 'good enough' match in the delta engine or vector store.
        """
        logger.info(f"soft_match: Attempting match for '{query}' (threshold={self.threshold})")
        
        # 1. Delta Engine handles some fuzzy matching already, but we check specifically for score
        # In a real implementation, delta_engine.find_delta might return a score
        delta = global_delta_engine_v2.find_delta(query)
        if delta:
            # If delta engine found something, it's usually high confidence
            logger.info("soft_match: Found delta match.")
            return {
                "answer": delta["answer"],
                "confidence": 0.9,
                "mode": "SOFT_MATCH_DELTA"
            }
            
        # 2. Vector Store fallback with lower threshold
        results = rag_search(query, k=1)
        if results:
            best_node = results[0]
            score = best_node.get("score", 0.0)
            if score >= self.threshold:
                logger.info(f"soft_match: Found vector match (score={score:.2f})")
                return {
                    "answer": best_node["content"],
                    "confidence": score,
                    "mode": "SOFT_MATCH_RAG"
                }
                
        logger.debug("soft_match: No match found above threshold.")
        return None

global_soft_match = SoftMatchEngine()
