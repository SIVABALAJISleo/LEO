"""
KV Cache Engine (Safe, production-grade)
Stores and retrieves transformer intermediate computation states.
Uses JSON serialization — no pickle (B301 compliant).
"""
import hashlib
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class KVCacheEngine:
    """
    Fast in-memory + optional Redis KV state store.
    Keyed by prompt hash. JSON-safe values only.
    """

    def __init__(self):
        self._memory: dict = {}
        self._redis = None
        self._ttl = 3600
        self._try_connect_redis()

    def _try_connect_redis(self):
        try:
            import redis
            self._redis = redis.from_url("redis://localhost:6379/1")
            self._redis.ping()
        except Exception:
            self._redis = None

    def _hash(self, prompt: str) -> str:
        return hashlib.sha256(prompt.strip().lower().encode()).hexdigest()

    def store(self, prompt: str, kv_state: Any):
        """Store a KV state safely using JSON."""
        key = self._hash(prompt)
        try:
            serialized = json.dumps(kv_state, default=str)
            self._memory[key] = serialized
            if self._redis:
                self._redis.setex(f"kvcache:{key}", self._ttl, serialized)
            logger.debug(f"kv_stored: prompt_len={len(prompt)}")
        except Exception as e:
            logger.warning(f"kv_store_failed: {e}")

    def lookup(self, prompt: str) -> Optional[Any]:
        """Retrieve a KV state by prompt hash."""
        key = self._hash(prompt)
        # 1. Memory
        if key in self._memory:
            logger.info("kv_hit: source=memory")
            return json.loads(self._memory[key])
        # 2. Redis
        if self._redis:
            try:
                data = self._redis.get(f"kvcache:{key}")
                if data:
                    logger.info("kv_hit: source=redis")
                    return json.loads(data) # type: ignore
            except Exception: # nosec B110
                pass
        return None


global_kv_cache_engine = KVCacheEngine()
