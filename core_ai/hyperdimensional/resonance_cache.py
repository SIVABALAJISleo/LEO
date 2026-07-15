"""
core_ai/hyperdimensional/resonance_cache.py
Semantic Resonance Cache (Instant Retrieval).
Maps queries directly to cached responses via HDC Hamming Distance.
Bypasses the entire LLM pipeline in <5ms.
"""

import numpy as np
import logging
from typing import Optional, Tuple
from .core import HyperdimensionalEncoder
from .igpu_accelerator import IGPUAccelerator

logger = logging.getLogger(__name__)

class ResonanceCache:
    def __init__(self, max_items: int = 10000, threshold: float = 0.3):
        self.encoder = HyperdimensionalEncoder()
        self.accelerator = IGPUAccelerator()
        self.max_items = max_items
        self.threshold = threshold
        
        # In-memory storage
        # Matrix of packed 1250-byte vectors
        self.memory_matrix = np.empty((0, self.encoder.byte_dim), dtype=np.uint8)
        self.payloads = [] # Array of dicts/strings
        
    def check_resonance(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Encodes the query and checks it against the cache using iGPU.
        Returns (True, response) if a match < threshold is found.
        """
        if self.memory_matrix.shape[0] == 0:
            return False, None
            
        query_vec = self.encoder.encode_text(query)
        
        # Calculate distances across all stored vectors
        distances = self.accelerator.calculate_hamming_distances(query_vec, self.memory_matrix)
        
        best_idx = np.argmin(distances)
        best_dist = distances[best_idx]
        
        if best_dist < self.threshold:
            logger.info(f"[Resonance] Cache HIT. Distance: {best_dist:.3f} < {self.threshold}")
            return True, self.payloads[best_idx]
            
        return False, None
        
    def update_cache(self, query: str, response: str):
        """
        Adds a new interaction to the cache. LRU eviction if max_items is reached.
        """
        query_vec = self.encoder.encode_text(query)
        
        if self.memory_matrix.shape[0] >= self.max_items:
            # Simple eviction: remove oldest 10%
            evict_count = self.max_items // 10
            self.memory_matrix = self.memory_matrix[evict_count:]
            self.payloads = self.payloads[evict_count:]
            
        self.memory_matrix = np.vstack([self.memory_matrix, query_vec])
        self.payloads.append(response)
