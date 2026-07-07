"""
User Behavior Predictor
Tracks per-user query sequences and predicts next queries.
Uses these predictions to warm caches proactively.
"""
import logging
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

# Common query sequences (next query given current intent)
SEQUENCE_PATTERNS = {
    "definition":  ["how_to", "comparison", "benefits"],
    "how_to":      ["definition", "explanation", "list"],
    "comparison":  ["definition", "how_to"],
    "explanation": ["definition", "how_to"],
    "list":        ["definition", "how_to"],
}

_MAX_HISTORY = 20  # Queries to remember per user


class UserProfiler:
    """
    Per-user query history tracker and next-query predictor.
    Enables proactive cache warming before users ask.
    """

    def __init__(self):
        self._histories: Dict[str, List[Dict]] = defaultdict(list)
        self._intent_sequences: Dict[str, Counter] = defaultdict(Counter)

    def record(self, user_id: str, query: str, shaped: Dict[str, Any]):
        """Record a query for a user."""
        history = self._histories[user_id]
        history.append({
            "query": query,
            "intent": shaped.get("intent", "general"),
            "entity": shaped.get("entity", "GENERAL"),
            "shape_key": shaped.get("shape_key", ""),
            "timestamp": time.time(),
        })
        # Keep rolling window
        if len(history) > _MAX_HISTORY:
            self._histories[user_id] = history[-_MAX_HISTORY:]

        # Track intent sequences
        if len(history) >= 2:
            prev_intent = history[-2]["intent"]
            curr_intent = shaped.get("intent", "general")
            self._intent_sequences[prev_intent][curr_intent] += 1

        logger.debug(f"user_profiled: user={user_id} intent={shaped.get('intent')}")

    def predict_next_intent(self, user_id: str) -> Optional[str]:
        """Predict the next likely intent for a user."""
        history = self._histories.get(user_id, [])
        if not history:
            return None

        last_intent = history[-1]["intent"]

        # Use learned sequences if available
        if last_intent in self._intent_sequences and self._intent_sequences[last_intent]:
            return self._intent_sequences[last_intent].most_common(1)[0][0]

        # Fall back to static patterns
        patterns = SEQUENCE_PATTERNS.get(last_intent, [])
        return patterns[0] if patterns else None

    def predict_next_entities(self, user_id: str) -> List[str]:
        """Predict entities the user is likely to query next."""
        history = self._histories.get(user_id, [])
        if len(history) < 2:
            return []

        # Return recent entities (likely to query again)
        recent_entities = [h["entity"] for h in history[-5:]]
        return list(dict.fromkeys(recent_entities))  # Deduplicated, order preserved

    def get_session_stats(self, user_id: str) -> Dict[str, Any]:
        history = self._histories.get(user_id, [])
        if not history:
            return {}
        intents = [h["intent"] for h in history]
        return {
            "query_count": len(history),
            "top_intent": Counter(intents).most_common(1)[0][0] if intents else None,
            "unique_entities": len(set(h["entity"] for h in history)),
        }


global_user_profiler = UserProfiler()
