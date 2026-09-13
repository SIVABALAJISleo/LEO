#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/pathway_search/semantic_cache.py
========================================
Phase 5: Separate Semantic Cache.
Can return APPROXIMATE, PREDICTIVE, or SEMANTIC_REUSE, but NEVER EXACT.
"""

import time
from typing import Dict, Any, Optional, Tuple, List
import numpy as np


class SemanticCacheEngine:
    """
    Semantic approximation cache based on embedding cosine similarity.
    Explicitly labeled as APPROXIMATE/PREDICTIVE.
    """

    def __init__(self, similarity_threshold: float = 0.95):
        self.similarity_threshold = similarity_threshold
        self.entries: List[Dict[str, Any]] = []

    def query(
        self,
        query_vector: np.ndarray
    ) -> Optional[Tuple[Any, float, Dict[str, Any]]]:
        """
        Returns: (cached_result, cosine_similarity, metadata) or None.
        """
        if not self.entries:
            return None

        q = np.asarray(query_vector, dtype=np.float32).flatten()
        q_norm = np.linalg.norm(q) + 1e-12
        q_unit = q / q_norm

        best_entry = None
        best_sim = -1.0

        for entry in self.entries:
            key_unit = entry["vector_unit"]
            sim = float(np.dot(q_unit, key_unit))
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_entry and best_sim >= self.similarity_threshold:
            meta = dict(best_entry["metadata"])
            meta["semantic_similarity"] = round(best_sim, 4)
            meta["correctness_class"] = "SEMANTIC_REUSE"
            return best_entry["result"], best_sim, meta

        return None

    def insert(
        self,
        vector: np.ndarray,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        v = np.asarray(vector, dtype=np.float32).flatten()
        v_norm = np.linalg.norm(v) + 1e-12
        self.entries.append({
            "vector_unit": v / v_norm,
            "result": result,
            "metadata": metadata or {}
        })
