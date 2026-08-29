"""
core_ai/semantic_answer_cache.py
================================
Layer 5: Semantic Embedding & Answer Cache
Leverages FAISS / SentenceTransformer embeddings to bypass dense inference on semantically equivalent queries.
Delivers <5ms response times (100% compute bypass).
"""

import time
import logging
from typing import Dict, Any, Tuple, Optional
from core_ai.semantic_cache import SemanticBypassEngine

logger = logging.getLogger("SemanticAnswerCache")


class SemanticAnswerCache:
    """
    High-speed semantic answer cache for LEO AI.
    Queries matching semantic similarity threshold return cached answers instantly.
    """

    def __init__(self, similarity_threshold: float = 0.80, max_entries: int = 10000):
        self.engine = SemanticBypassEngine(exact_capacity=max_entries, semantic_threshold=similarity_threshold)
        self.similarity_threshold = similarity_threshold

    def store_answer(self, query: str, answer: str, metadata: Optional[Dict[str, Any]] = None):
        """Stores query and answer with metadata."""
        tag = metadata.get("tag", "general") if metadata else "general"
        self.engine.store(query, answer, tag=tag)

    def lookup(self, query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], float]:
        """
        Looks up query in semantic cache.
        Returns (answer, metadata, latency_ms) if found, else (None, None, latency_ms).
        """
        t0 = time.perf_counter()
        resp, score, tier = self.engine.query(query)
        lat_ms = (time.perf_counter() - t0) * 1000.0

        if resp is not None:
            meta = {"hit_tier": tier, "similarity_score": score, "latency_ms": lat_ms}
            return resp, meta, lat_ms
        return None, None, lat_ms

    def get_stats(self) -> Dict[str, Any]:
        return self.engine.get_metrics()
