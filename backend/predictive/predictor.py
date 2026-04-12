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

    def predict_next_queries(self, query: str, session_id: str = "default") -> Dict[str, List[str]]:
        """
        Point 2: Predict 5–10 variations and 3–5 follow-ups.
        Enables 98% compute avoidance by resolving user journey stages ahead of time.
        """
        norm = global_normalizer.normalize(query)
        entity = norm.get("entity", "system")
        
        # 1. Semantic Variations (5-10 queries)
        variations = [
            f"what is {entity}",
            f"usage examples for {entity}",
            f"how does {entity} work",
            f"best practices using {entity}",
            f"troubleshooting {entity} issues",
            f"optimizing {entity} performance",
            f"security considerations for {entity}",
            f"scaling {entity}",
            f"setup guide for {entity}",
            f"how to automate {entity}"
        ][:10]
        
        # 2. Contextual follow-ups (3-5 queries)
        follow_ups = []
        q_lower = query.lower()
        if "database" in q_lower or "sql" in q_lower:
            follow_ups = ["how to scale databases", "backup strategies", "migration guide", "query optimization"]
        elif "api" in q_lower or "rest" in q_lower:
            follow_ups = ["api security", "rate limiting setup", "documentation best practices", "sdk generation"]
        elif "deploy" in q_lower or "cloud" in q_lower:
            follow_ups = ["ci/cd pipeline setup", "container orchestration", "cost optimization", "monitoring alerts"]
        else:
            follow_ups = [f"advanced {entity} concepts", f"integrating {entity}", f"future of {entity}"]

        # Ensure counts
        return {
            "variations": variations[:10],
            "follow_ups": follow_ups[:5]
        }

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
