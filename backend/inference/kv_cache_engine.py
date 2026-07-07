"""
backend/inference/kv_cache_engine.py
Layer 3 — Skip Sequential Token Steps: KV Cache Engine.

Stores and retrieves transformer intermediate computation states.
Features prefix-matching reuse to share/reuse KV caches across speculative branches
and crystallization cache hits, avoiding recomputation on partial matches.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Optional, Any, Tuple, Dict

logger = logging.getLogger(__name__)


class KVCacheEngine:
    """
    Fast in-memory + optional Redis KV state store.
    Keyed by prompt hash. Supports prefix matching for KV-state reuse.
    """

    def __init__(self):
        self._memory: Dict[str, str] = {}
        # Keep a mapping of raw prompt to its hash to allow prefix matching
        self._prompts: Dict[str, str] = {}
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
        normalized = prompt.strip().lower()
        key = self._hash(normalized)
        try:
            serialized = json.dumps(kv_state, default=str)
            self._memory[key] = serialized
            self._prompts[normalized] = key
            
            if self._redis:
                self._redis.setex(f"kvcache:{key}", self._ttl, serialized)
                self._redis.setex(f"kvcache_prompt:{key}", self._ttl, normalized)
                
            logger.debug(f"kv_stored: prompt_len={len(prompt)}")
        except Exception as e:
            logger.warning(f"kv_store_failed: {e}")

    def lookup(self, prompt: str) -> Optional[Any]:
        """Retrieve a KV state by exact prompt hash."""
        normalized = prompt.strip().lower()
        key = self._hash(normalized)
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
            except Exception:
                pass
        return None

    def match_prefix(self, prompt: str) -> Tuple[int, Optional[Any]]:
        """
        Looks for the longest cached prompt that is a prefix of the input prompt.
        Returns (prefix_length_in_characters, kv_state).
        Used for sharing prefix KV states across speculative branches / crystallization hits.
        """
        normalized = prompt.strip().lower()
        
        # Check exact lookup first
        exact_state = self.lookup(prompt)
        if exact_state is not None:
            return len(prompt), exact_state
            
        # Scan cached prompts for prefix matches
        best_prefix = ""
        best_key = ""
        
        for cached_prompt in self._prompts:
            if normalized.startswith(cached_prompt) and len(cached_prompt) > len(best_prefix):
                best_prefix = cached_prompt
                best_key = self._prompts[cached_prompt]
                
        if best_prefix:
            logger.info(f"kv_prefix_match_hit: matched_chars={len(best_prefix)}")
            return len(best_prefix), json.loads(self._memory[best_key])
            
        return 0, None


global_kv_cache_engine = KVCacheEngine()
