"""
Global Reasoning Memory
Stores reasoning steps for past queries so similar future queries can
reuse the same reasoning path without re-executing.
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

_MEMORY_LIMIT = 10_000  # Max entries to prevent unbounded growth


class ReasoningStore:
    """
    In-memory store of {query_hash → {steps, answer, confidence}}.
    Provides fuzzy-match style retrieval based on normalized query signature.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def _key(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()

    def store(self, query: str, steps: List[str], answer: str, confidence: float = 0.9):
        """Stores a reasoning trace keyed by query hash."""
        if len(self._store) >= _MEMORY_LIMIT:
            # Evict oldest 10%
            oldest_keys = list(self._store.keys())[: _MEMORY_LIMIT // 10]
            for k in oldest_keys:
                del self._store[k]

        key = self._key(query)
        self._store[key] = {
            "query": query,
            "steps": steps,
            "answer": answer,
            "confidence": confidence,
            "reuses": 0,
        }
        logger.debug(f"reasoning_stored: query_len={len(query)}")

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """Looks up an exact-match reasoning trace."""
        key = self._key(query)
        entry = self._store.get(key)
        if entry:
            entry["reuses"] += 1
            logger.info(f"reasoning_hit: reuses={entry['reuses']}")
            return entry
        return None

    def stats(self) -> Dict[str, int]:
        return {
            "total_stored": len(self._store),
            "total_reuses": sum(e["reuses"] for e in self._store.values()),
        }


global_reasoning_store = ReasoningStore()
