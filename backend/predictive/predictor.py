import logging
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class PredictivePredictor:
    """
    Core engine for mining query patterns and clustering semantically similar requests.
    Identifies 'hot' canonical queries for Layer 1 precomputation.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()
        self.history = [] # In-memory buffer for demonstration, real system uses DB logs

    def log_query(self, query: str):
        self.history.append(query)
        if len(self.history) > 100:
            self.history.pop(0)

    def mine_patterns(self) -> List[str]:
        """
        Extracts high-frequency canonical questions from query logs.
        Uses semantic clustering to group variations of the same intent.
        """
        if not self.history:
            return []
            
        # 1. Semantic Clustering
        embeddings = self.semantic_cache.model.encode(self.history)
        
        # Simple Clustering (K-Means/Agglomerative would be used at scale)
        # Here we use a similarity-based grouping
        canonical_queries = []
        processed = set()
        
        for i, query in enumerate(self.history):
            if i in processed: continue
            
            # Find similar queries to the current one
            sim_indices = []
            for j in range(i + 1, len(self.history)):
                if j in processed: continue
                # Cosine similarity
                sim = np.dot(embeddings[i], embeddings[j])
                if sim > 0.90:
                    sim_indices.append(j)
                    processed.add(j)
            
            if len(sim_indices) >= 2: # Pattern detected
                canonical_queries.append(query)
                processed.add(i)
                
        return canonical_queries

global_predictor = PredictivePredictor()
