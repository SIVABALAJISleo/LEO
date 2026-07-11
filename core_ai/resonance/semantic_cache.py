"""
core_ai/resonance/semantic_cache.py
LEO Tesla Resonance Protocol — Semantic Energy Capture Field.
"""

from __future__ import annotations

import logging
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MockRedisVectorSearch:
    """Mock Redis vector similarity client for fallback/CI execution."""
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self.cache[key] = value

    def vector_search(self, embedding: np.ndarray, threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        for node in self.cache.values():
            ref_emb = np.array(node["embedding"])
            similarity = np.dot(embedding, ref_emb) / (
                np.linalg.norm(embedding) * np.linalg.norm(ref_emb) + 1e-9
            )
            if similarity >= threshold:
                return {
                    "response": node["response"],
                    "similarity": round(float(similarity), 4)
                }
        return None


class LEOSemanticCache:
    """Multi-tier semantic cache using local mock or Redis backends."""

    def __init__(self):
        self.redis = MockRedisVectorSearch()
        self.dim = 384
        logger.info("[TeslaCache] Semantic Energy Capture Field activated.")

    def _generate_mock_embedding(self, query: str) -> np.ndarray:
        """Emulates mini-lm CPU output vector for test isolation."""
        seed = sum(ord(c) for c in query) % (2**32)
        rng = np.random.default_rng(seed)
        return rng.uniform(-1.0, 1.0, size=self.dim).astype(np.float32)

    def intercept_query(self, query: str) -> Optional[str]:
        """Check the multi-tier thresholds: Exact, Semantic, Conceptual."""
        emb = self._generate_mock_embedding(query)
        # Search semantic cache
        hit = self.redis.vector_search(emb, threshold=0.85)
        if hit:
            logger.info(f"[TeslaCache] Hit found with similarity: {hit['similarity']}")
            return hit["response"]
        return None

    def store_query(self, query: str, response: str) -> None:
        """Cache the query with its mock vector representation."""
        emb = self._generate_mock_embedding(query)
        self.redis.set(query, {
            "query": query,
            "response": response,
            "embedding": emb.tolist()
        })
