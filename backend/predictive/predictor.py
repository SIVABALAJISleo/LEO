import logging
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
from backend.intelligence.router import SemanticCache
from backend.normalization.normalizer import global_normalizer

logger = logging.getLogger(__name__)

class PredictivePredictor:
    """
    Advanced Prediction Engine (Layer 0).
    Points 2 & 3: Predict next 5–15 queries based on intent, variations, and session history.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()
        self.session_history: Dict[str, List[str]] = {} # session_id -> list of queries
        self.global_history: List[str] = []

    def log_query(self, session_id: str, query: str):
        """Unified logging for session and global history."""
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        self.session_history[session_id].append(query)
        self.global_history.append(query)
        
        # Buffer management
        if len(self.session_history[session_id]) > 20: self.session_history[session_id].pop(0)
        if len(self.global_history) > 100: self.global_history.pop(0)

    def predict_next_queries(self, query: str, session_id: str = "default", count: int = 12) -> List[str]:
        """
        AI Systems Architect (Point 3): Predict 5–15 queries.
        Includes semantic variations, follow-ups, and common pitfalls.
        """
        norm = global_normalizer.normalize(query)
        intent = norm["intent"]
        entity = norm["entity"]
        
        # 1. Semantic Variations (Point 3 & 13)
        # Generate diverse phrasing to hit 0.85 semantic clustering
        variations = [
            f"what is {entity}",
            f"usage examples for {entity}",
            f"how does {entity} work",
            f"best practices using {entity}",
            f"troubleshooting {entity} issues",
            f"optimizing {entity} performance",
            f"security considerations for {entity}",
            f"scaling {entity} globally",
            f"cost of {entity} implementation",
            f"alternatives to {entity}",
            f"advantages of {entity} vs others",
            f"is {entity} enterprise ready",
            f"roadmap for {entity}",
            f"setup guide for {entity}",
            f"how to automate {entity}"
        ]
        
        # 2. Contextual follow-ups based on session
        follow_ups = []
        if session_id in self.session_history:
            # Add logic for transition prediction (A -> B)
            # For this layer, we use rule-based expansion
            if any(w in query.lower() for w in ["database", "sql", "nosql"]):
                follow_ups.append("database migration steps")
                follow_ups.append("backup and recovery strategies")
            if any(w in query.lower() for w in ["api", "rest", "graphql"]):
                follow_ups.append("authentication strategies")
                follow_ups.append("rate limiting benchmarks")

        # 3. Combine and filter
        all_preds = list(set(variations + follow_ups))
        
        # AI Architect: Ensure 5-15 count range
        final_count = max(5, min(count, 15))
        predictions = all_preds[:final_count]
        
        logger.info(f"predictor_forecasting: query='{query}' -> {len(predictions)} variations generated.")
        return predictions

    def mine_patterns(self) -> List[str]:
        """Global pattern mining for background precomputation."""
        all_queries = [q for history in self.session_history.values() for q in history]
        if not all_queries:
            return []
            
        embeddings = self.semantic_cache.model.encode(all_queries)
        canonical_queries = []
        processed = set()
        
        for i, query in enumerate(all_queries):
            if i in processed: continue
            sim_indices = []
            for j in range(i + 1, len(all_queries)):
                if j in processed: continue
                sim = np.dot(embeddings[i], embeddings[j])
                if sim > 0.85: # Aligned with Phase 30 threshold
                    sim_indices.append(j)
                    processed.add(j)
            
            if len(sim_indices) >= 2:
                canonical_queries.append(query)
                processed.add(i)
                
        return canonical_queries

global_predictor = PredictivePredictor()
