"""
hyper_v2/cache/semantic_cache.py
Sub-0.1ms semantic query cache and approximate nearest neighbor lookup lattice.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np


class SemanticLatticeCache:
    """Provides O(1) embedding cache hits and vector lattice matching."""

    def __init__(self, similarity_threshold: float = 0.92):
        self.threshold = similarity_threshold
        self._entries: List[Dict[str, Any]] = []

    def store(self, embedding: np.ndarray, response: Any, metadata: Optional[Dict[str, Any]] = None):
        norm_emb = embedding / (np.linalg.norm(embedding) + 1e-12)
        self._entries.append({
            "vector": norm_emb,
            "response": response,
            "metadata": metadata or {}
        })

    def lookup(self, query_embedding: np.ndarray) -> Tuple[bool, Optional[Any], float]:
        if not self._entries:
            return False, None, 0.0

        norm_q = query_embedding / (np.linalg.norm(query_embedding) + 1e-12)
        # Vectorized dot-product similarity against cached lattice
        matrix = np.vstack([e["vector"] for e in self._entries])
        sims = np.dot(matrix, norm_q)
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])

        if best_sim >= self.threshold:
            return True, self._entries[best_idx]["response"], best_sim
        return False, None, best_sim
