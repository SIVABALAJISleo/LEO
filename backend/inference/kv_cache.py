import logging
import json
import numpy as np
from typing import Optional, Dict, Any, Tuple
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class KVCacheEngine:
    """
    Engine for storing and reusing transformer KV-states based on prompt similarity.
    Reduces redundant computation for shared prompt prefixes.
    Uses JSON serialization instead of pickle to prevent security vulnerabilities (B301).
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._local_fallback: Dict[str, Any] = {}
        self._prompts: Dict[str, str] = {}
        try:
            import redis as redis_lib
            self.redis = redis_lib.from_url(redis_url)
            # Test connection
            self.redis.ping()
        except Exception:
            self.redis = None
            import os
            if not os.getenv("CI"):
                logger.warning("kv_cache: Redis unavailable, using local fallback.")
        self.semantic_cache = SemanticCache()
        self.ttl = 3600  # 1 hour TTL for KV states

    def store_kv_state(self, prompt: str, kv_state: Any, metadata: Optional[Dict[str, Any]] = None):
        prompt_hash = self._get_hash(prompt)
        normalized = prompt.strip().lower()
        
        # Always store in local fallback as a safety
        self._local_fallback[f"kv_cache:{prompt_hash}"] = kv_state
        self._prompts[normalized] = prompt_hash

        if not self.redis:
            return
        try:
            if isinstance(kv_state, np.ndarray):
                serialized_kv = json.dumps(kv_state.tolist())
            elif hasattr(kv_state, '__dict__'):
                serialized_kv = json.dumps(str(kv_state))
            else:
                serialized_kv = json.dumps(kv_state)

            self.redis.setex(f"kv_cache:{prompt_hash}", self.ttl, serialized_kv)
            logger.info(f"kv_cache_stored: prompt_len={len(prompt)}")
        except Exception as e:
            logger.warning(f"kv_cache_store_failed (falling back to local): {e}")

    def lookup_kv_state(self, prompt: str) -> Optional[Any]:
        prompt_hash = self._get_hash(prompt)
        
        # Check Redis if available
        if self.redis:
            try:
                data = self.redis.get(f"kv_cache:{prompt_hash}")
                if data:
                    logger.info("kv_cache_hit: prefix_reuse_active (Redis)")
                    return json.loads(data) # type: ignore
            except Exception as e:
                logger.warning(f"kv_cache_lookup_failed: {e}")
        
        # Check local fallback
        local_data = self._local_fallback.get(f"kv_cache:{prompt_hash}")
        if local_data is not None:
            logger.info("kv_cache_hit: prefix_reuse_active (Local Fallback)")
            return local_data

        return None

    def match_prefix(self, prompt: str) -> Tuple[int, Optional[Any]]:
        """
        Scan cached prompts for prefix matches.
        """
        normalized = prompt.strip().lower()
        exact_match = self.lookup_kv_state(prompt)
        if exact_match is not None:
            return len(prompt), exact_match
            
        best_prefix = ""
        best_hash = ""
        for cached in self._prompts:
            if normalized.startswith(cached) and len(cached) > len(best_prefix):
                best_prefix = cached
                best_hash = self._prompts[cached]
                
        if best_prefix:
            logger.info(f"kv_prefix_match_hit: matched_chars={len(best_prefix)}")
            return len(best_prefix), self._local_fallback.get(f"kv_cache:{best_hash}")
            
        return 0, None

    def _get_hash(self, text: str) -> str:
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()

global_kv_cache = KVCacheEngine()
