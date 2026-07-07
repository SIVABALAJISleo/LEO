"""
backend/memory/contextual_memory_stack.py

Contextual Memory Stack (AIS++ Module 5)
=========================================
Three-layer memory architecture routed in strict order:

  Layer 1 → User-level memory    (personalized, persistent per user)
  Layer 2 → Session-level memory (active conversation context)
  Layer 3 → Global-level memory  (shared across all users)

Routing rule:
  Try user → session → global. Return on first confident hit.
  Each layer uses confidence gating (≥ 0.95 for user/session, ≥ 0.88 for global).

Rules:
  - Every answer stored at all appropriate layers simultaneously
  - User memory improves with each interaction (reinforcement)
  - Session memory is ephemeral (TTL = session duration)
  - Global memory is shared and permanent
"""
import logging
import time
import json
import os
from typing import Dict, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

USER_MEMORY_PATH  = os.path.join(os.getcwd(), "data", "user_memory.json")
USER_CONFIDENCE_FLOOR    = 0.95
SESSION_CONFIDENCE_FLOOR = 0.90
GLOBAL_CONFIDENCE_FLOOR  = 0.88
SESSION_TTL_SECONDS      = 3600   # 1 hour


class UserMemoryLayer:
    """
    Layer 1: Per-user persistent knowledge.
    Maps user_id → {family_id → answer_entry}.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._load()

    def get(self, user_id: str, family_id: str) -> Optional[Dict[str, Any]]:
        user_data = self._store.get(user_id, {})
        entry = user_data.get(family_id)
        if entry and entry.get("confidence", 0) >= USER_CONFIDENCE_FLOOR:
            entry["hits"] = entry.get("hits", 0) + 1
            logger.debug(f"user_mem.hit: user={user_id} family={family_id}")
            return entry
        return None

    def set(self, user_id: str, family_id: str, answer: str, confidence: float, query: str) -> None:
        if user_id not in self._store:
            self._store[user_id] = {}
        existing = self._store[user_id].get(family_id)
        # Only overwrite if new confidence is higher
        if existing and existing.get("confidence", 0) >= confidence:
            existing["hits"] = existing.get("hits", 0) + 1
            return
        self._store[user_id][family_id] = {
            "answer": answer,
            "confidence": confidence,
            "query": query,
            "hits": 1,
            "stored_at": time.time(),
        }
        self._save()

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(USER_MEMORY_PATH), exist_ok=True)
            with open(USER_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(self._store, f)
        except Exception as exc:
            logger.warning(f"user_mem.save_error: {exc}")

    def _load(self) -> None:
        if not os.path.exists(USER_MEMORY_PATH):
            return
        try:
            with open(USER_MEMORY_PATH, "r", encoding="utf-8") as f:
                self._store = json.load(f)
            logger.info(f"user_mem.loaded: users={len(self._store)}")
        except Exception as exc:
            logger.warning(f"user_mem.load_error: {exc}")

    def stats(self) -> Dict[str, Any]:
        total_entries = sum(len(v) for v in self._store.values())
        return {
            "users": len(self._store),
            "total_entries": total_entries,
        }


class SessionMemoryLayer:
    """
    Layer 2: Per-session ephemeral context.
    Maps session_id → {family_id → answer_entry}.
    Entries expire after SESSION_TTL_SECONDS.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self._session_start: Dict[str, float] = {}

    def get(self, session_id: str, family_id: str) -> Optional[Dict[str, Any]]:
        self._evict_if_expired(session_id)
        entry = self._store.get(session_id, {}).get(family_id)
        if entry and entry.get("confidence", 0) >= SESSION_CONFIDENCE_FLOOR:
            logger.debug(f"session_mem.hit: session={session_id} family={family_id}")
            return entry
        return None

    def set(self, session_id: str, family_id: str, answer: str, confidence: float, query: str) -> None:
        if session_id not in self._session_start:
            self._session_start[session_id] = time.time()
        self._store[session_id][family_id] = {
            "answer": answer,
            "confidence": confidence,
            "query": query,
            "stored_at": time.time(),
        }

    def _evict_if_expired(self, session_id: str) -> None:
        start = self._session_start.get(session_id)
        if start and (time.time() - start) > SESSION_TTL_SECONDS:
            self._store.pop(session_id, None)
            self._session_start.pop(session_id, None)
            logger.debug(f"session_mem.evicted: session={session_id}")

    def stats(self) -> Dict[str, Any]:
        return {
            "active_sessions": len(self._store),
            "total_items": sum(len(v) for v in self._store.values()),
        }


class ContextualMemoryStack:
    """
    Three-layer memory router.
    Routes queries to the most personalized available memory layer first.
    """

    def __init__(self):
        self.user_layer    = UserMemoryLayer()
        self.session_layer = SessionMemoryLayer()
        # Global layer is provided externally (global_memory from global_memory.py)
        self._lookups: int = 0
        self._hits: Dict[str, int] = {"user": 0, "session": 0, "global": 0, "miss": 0}

    def lookup(
        self,
        family_id: str,
        query: str,
        user_id: str,
        session_id: str,
        global_memory,
    ) -> Optional[Dict[str, Any]]:
        """
        Tries all 3 layers in order. Returns on first confident hit.

        Layer priority: user → session → global
        """
        self._lookups += 1

        # Layer 1: User memory
        hit = self.user_layer.get(user_id, family_id)
        if hit:
            self._hits["user"] += 1
            return {**hit, "memory_layer": "user"}

        # Layer 2: Session memory
        hit = self.session_layer.get(session_id, family_id)
        if hit:
            self._hits["session"] += 1
            return {**hit, "memory_layer": "session"}

        # Layer 3: Global memory
        try:
            hit = global_memory.lookup(query, canonical_form=family_id)
            if hit and hit.get("confidence", 0) >= GLOBAL_CONFIDENCE_FLOOR:
                self._hits["global"] += 1
                logger.info(
                    f"memory_stack.global_hit: family={family_id} "
                    f"conf={hit.get('confidence', 0):.3f}"
                )
                return {**hit, "memory_layer": "global"}
        except Exception as exc:
            logger.warning(f"memory_stack.global_lookup_error: {exc}")

        self._hits["miss"] += 1
        return None

    def store(
        self,
        family_id: str,
        query: str,
        answer: str,
        confidence: float,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Stores answer in all applicable layers simultaneously.
        - Always stores in session layer
        - Stores in user layer for high-confidence results
        - Global layer storage is handled by zero_repeat_store separately
        """
        self.session_layer.set(session_id, family_id, answer, confidence, query)

        if confidence >= USER_CONFIDENCE_FLOOR:
            self.user_layer.set(user_id, family_id, answer, confidence, query)

        logger.debug(
            f"memory_stack.stored: family={family_id} "
            f"user={user_id} session={session_id} conf={confidence:.3f}"
        )

    def stats(self) -> Dict[str, Any]:
        total = self._lookups or 1
        hit_rate = (self._lookups - self._hits["miss"]) / total
        return {
            "total_lookups": self._lookups,
            "hit_distribution": self._hits,
            "overall_hit_rate": f"{hit_rate:.2%}",
            "user_layer":    self.user_layer.stats(),
            "session_layer": self.session_layer.stats(),
        }


global_memory_stack = ContextualMemoryStack()
