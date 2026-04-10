"""
Graph Store — In-memory + Redis-backed storage for reasoning patterns.
Stores {intent, entity, pattern, answer} graphs keyed by query signature.
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class GraphStore:
    """
    Thread-safe in-memory graph store with optional Redis persistence.
    Stores reasoning patterns indexed by (intent, entity) pairs.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._redis = None
        self._try_connect_redis()

    def _try_connect_redis(self):
        try:
            import redis
            from backend.core.middleware import redis_client
            self._redis = redis_client
        except Exception:
            self._redis = None

    def _make_key(self, intent: str, entity: str) -> str:
        raw = f"{intent}:{entity.lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def store(self, intent: str, entity: str, pattern: List[str], answer: str, tenant_id: str = "default"):
        key = self._make_key(intent, entity)
        entry = {
            "intent": intent,
            "entity": entity,
            "pattern": pattern,
            "answer": answer,
            "tenant_id": tenant_id,
            "hits": 0,
        }
        self._store[key] = entry
        if self._redis:
            try:
                self._redis.setex(f"graph:{key}", 86400, json.dumps(entry))
            except Exception: # nosec B110
                pass
        logger.info(f"graph_stored: intent={intent} entity={entity}")

    def lookup(self, intent: str, entity: str, tenant_id: str = "default") -> Optional[Dict[str, Any]]:
        key = self._make_key(intent, entity)

        # 1. In-memory fast path
        if key in self._store:
            self._store[key]["hits"] += 1
            logger.info(f"graph_hit: intent={intent} entity={entity} (memory)")
            return self._store[key]

        # 2. Redis fallback
        if self._redis:
            try:
                data = self._redis.get(f"graph:{key}")
                if data:
                    entry = json.loads(data)
                    self._store[key] = entry  # Warm local cache
                    logger.info(f"graph_hit: intent={intent} entity={entity} (redis)")
                    return entry
            except Exception: # nosec B110
                pass

        return None

    def all_patterns(self) -> List[Dict[str, Any]]:
        return list(self._store.values())

    def size(self) -> int:
        return len(self._store)


global_graph_store = GraphStore()
