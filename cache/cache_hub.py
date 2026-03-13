import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class UniversalCacheHub:
    """
    Centralized caching for results, queries, and perceptual frames.
    """
    def __init__(self, ttl: int = 3600):
        self.store: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self.store.get(key)
        if not entry:
            return None
            
        if time.time() - entry["ts"] > self.ttl:
            del self.store[key]
            return None
            
        logger.info(f"Cache Hit: {key}")
        return entry["data"]

    def set(self, key: str, value: Any):
        self.store[key] = {
            "data": value,
            "ts": time.time()
        }
        logger.info(f"Cache Store: {key}")

    def purge_expired(self):
        now = time.time()
        expired = [k for k, v in self.store.items() if now - v["ts"] > self.ttl]
        for k in expired:
            del self.store[k]
