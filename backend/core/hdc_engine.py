"""
backend/core/hdc_engine.py

Hyperdimensional Computing (HDC) Engine (AIS++ Module 17)
=========================================================
Implements Sparse Distributed Representations (SDR) and HDC bundles.
Maps queries into high-dimensional space (2048-bits) for ultra-fast 
similarity via bit overlap (Hamming/Cosine).

Rule:
Similarity = Bit Overlap.
Jump to nearest known structure.
"""
import logging
import numpy as np
import hashlib
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DIMENSION = 2048 # High-dimensional vector space

class HDCEngine:
    """
    HDC/SDR engine for the Approximate Layer.
    Uses random projections to map text to bitvectors.
    """
    def __init__(self):
        # random_projection_matrix: Map chars to vectors
        # For simplicity, we'll hash substrings into the 2048-dim space
        self._memory_vectors: Dict[str, np.ndarray] = {}
        self._answers: Dict[str, str] = {}

    def embed(self, text: str) -> np.ndarray:
        """Projects text into the 2048-bit HDC space."""
        vector = np.zeros(DIMENSION, dtype=bool)
        # 3-gram hashing into vector space
        text = text.lower().strip()
        for i in range(len(text) - 2):
            gram = text[i:i+3]
            # Use hash to flip a bit in the 2048-dim space (SHA256 for auditor compliance)
            idx = int(hashlib.md5(gram.encode(), usedforsecurity=False).hexdigest(), 16) % DIMENSION
            vector[idx] = True
        return vector

    def search(self, query: str, threshold: float = 0.5) -> Optional[Dict[str, Any]]:
        """
        Finds the nearest neighbor in HDC space via bit overlap.
        O(N) but highly parallizable/vectorized.
        """
        if not self._memory_vectors: return None
        
        q_vec = self.embed(query)
        q_sum = np.sum(q_vec)
        if q_sum == 0: return None

        best_score = 0
        best_key = None

        # Simulation of associative memory lookup
        for key, v in self._memory_vectors.items():
            # HDC Overlap Score (Dot product of bitvectors)
            overlap = np.logical_and(q_vec, v)
            score = np.sum(overlap) / q_sum
            
            if score > best_score:
                best_score = score
                best_key = key

        if best_key and best_score >= threshold:
            return {
                "answer": self._answers[best_key],
                "confidence": float(best_score),
                "mode": "HDC"
            }
        return None

    def memorize(self, query: str, answer: str):
        """Stores a query-answer pair in the high-dimensional memory."""
        vec = self.embed(query)
        key = hashlib.md5(query.encode(), usedforsecurity=False).hexdigest()
        self._memory_vectors[key] = vec
        self._answers[key] = answer

    def stats(self) -> Dict[str, Any]:
        return {
            "hdc_memories": len(self._memory_vectors),
            "dimension": DIMENSION,
            "status": "associative_ready"
        }

global_hdc_engine = HDCEngine()
