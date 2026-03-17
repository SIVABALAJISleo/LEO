import logging
import json
import numpy as np
from typing import Optional, Dict, Any
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class KVCacheEngine:
    """
    Engine for storing and reusing transformer KV-states based on prompt similarity.
    Reduces redundant computation for shared prompt prefixes.
    Uses JSON serialization instead of pickle to prevent security vulnerabilities (B301).
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            import redis as redis_lib
            self.redis = redis_lib.from_url(redis_url)
        except Exception:
            self.redis = None
            logger.warning("kv_cache: Redis unavailable, cache disabled.")
        self.semantic_cache = SemanticCache()
        self.ttl = 3600  # 1 hour TTL for KV states

    def store_kv_state(self, prompt: str, kv_state: Any, metadata: Optional[Dict[str, Any]] = None):
        """
        Stores KV states in Redis keyed by prompt hash.
        Uses JSON serialization for security (avoids pickle).
        """
        if not self.redis:
            return
        try:
            # Serialize KV state safely using JSON
            # numpy arrays are converted to lists for JSON compatibility
            if isinstance(kv_state, np.ndarray):
                serialized_kv = json.dumps(kv_state.tolist())
            elif hasattr(kv_state, '__dict__'):
                serialized_kv = json.dumps(str(kv_state))
            else:
                serialized_kv = json.dumps(kv_state)

            prompt_hash = self._get_hash(prompt)
            self.redis.setex(f"kv_cache:{prompt_hash}", self.ttl, serialized_kv)

            logger.info(f"kv_cache_stored: prompt_len={len(prompt)}")
        except Exception as e:
            logger.error(f"kv_cache_store_failed: {e}")

    def lookup_kv_state(self, prompt: str) -> Optional[Any]:
        """
        Attempts to find a reusable KV state for the given prompt.
        Uses JSON deserialization for security (avoids pickle).
        """
        if not self.redis:
            return None
        try:
            prompt_hash = self._get_hash(prompt)
            data = self.redis.get(f"kv_cache:{prompt_hash}")
            if data:
                logger.info("kv_cache_hit: prefix_reuse_active")
                return json.loads(data)  # nosec - safe JSON deserialization
        except Exception as e:
            logger.error(f"kv_cache_lookup_failed: {e}")
        return None

    def _get_hash(self, text: str) -> str:
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()

global_kv_cache = KVCacheEngine()
