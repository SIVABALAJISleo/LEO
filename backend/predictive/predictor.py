import logging
import asyncio
from typing import List, Dict
from backend.normalization.normalizer import global_normalizer

logger = logging.getLogger(__name__)

HOT_QUERIES = ["what is ai", "explain hyper architecture", "leo system status", "api reference"]

class PredictivePredictor:
    """
    Advanced Prediction Engine (Layer 0).
    Context-aware variation generation based on session + trends.
    """
    def __init__(self):
        self.session_history: Dict[str, List[str]] = {}

    def log_query(self, session_id: str, query: str):
        """Unified logging for session and global history."""
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        self.session_history[session_id].append(query)
        
        # Buffer management
        if len(self.session_history[session_id]) > 20: self.session_history[session_id].pop(0)

    def predict_next_queries(self, query: str, session_id: str = "default") -> Dict[str, List[str]]:
        """Adaptive prediction based on session context."""
        if session_id not in self.session_history: self.session_history[session_id] = []
        self.session_history[session_id].append(query)
        
        norm = global_normalizer.normalize(query)
        entity = norm.get("entity", "system")
        
        # 1. Trending & Hot Dominance (Point 5)
        variations = [q for q in HOT_QUERIES if entity.lower() in q]
        
        # 2. Session Context (Point 6)
        history = self.session_history[session_id]
        if len(history) > 1:
            # Predict based on transition
            variations += [f"how to implement {entity}", f"advanced {entity} tutorial"]
        
        # 3. Mass Paraphrases
        variations += [f"definition of {entity}", f"simple {entity} explanation", f"troubleshoot {entity}"]

        return {
            "variations": list(set(variations[:20])),
            "follow_ups": [f"next steps for {entity}", f"scaling {entity} in production"]
        }

    def mine_patterns(self) -> List[str]:
        """Returns a list of frequently occurring query patterns to precompute."""
        # Derive patterns from HOT_QUERIES and session activity
        hot = list(HOT_QUERIES)
        session_queries = [
            q for history in self.session_history.values()
            for q in history
        ]
        # Pick the most recent session queries (unique)
        seen = set()
        for q in reversed(session_queries):
            if q not in seen:
                seen.add(q)
                hot.append(q)
            if len(hot) >= 30:
                break
        return hot

    async def preload(self, partial_query: str, session_id: str, tenant_id: str):
        """
        Point 10: CONTEXT PRELOADING.
        Start processing before request completes (predict while typing).
        """
        if len(partial_query) < 4: return
        
        # Predict candidate full queries
        norm = global_normalizer.normalize(partial_query)
        entity = norm.get("entity", "GENERIC")
        candidates = [f"what is {entity}", f"how to use {entity}"]
        
        from backend.background.compute_engine import global_bg_compute
        for q in candidates:
            # Heat up the cache for likely candidates
            asyncio.create_task(global_bg_compute.enqueue(q, tenant_id, "SYSTEM", session_id, priority="predicted"))
            
        logger.info(f"cis_preload: Context pre-warmed for '{partial_query}'")

global_predictor = PredictivePredictor()
