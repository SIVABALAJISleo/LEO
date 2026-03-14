import hashlib
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Reusing the existing redis_client from middleware
from backend.core.middleware import redis_client

def get_prompt_hash(prompt: str):
    """Generates a stable SHA-256 hash for the prompt."""
    return hashlib.sha256(prompt.encode()).hexdigest()

def check_cache(prompt: str, tenant_id: str = "default") -> Optional[str]:
    """Checks the exact prompt cache for a hit."""
    if not redis_client:
        return None
    
    key = f"prompt_cache:{tenant_id}:{get_prompt_hash(prompt)}"
    try:
        cached = redis_client.get(key)
        if cached:
            if hasattr(cached, 'decode'):
                cached = cached.decode('utf-8')
            logger.info(f"prompt_cache_hit: tenant={tenant_id}")
            return cached
    except Exception as e:
        logger.warning(f"prompt_cache_check_failed: {e}")
    return None

def save_cache(prompt: str, response: str, tenant_id: str = "default", ttl: int = 3600):
    """Saves the prompt response to the cache with 1 hour TTL."""
    if not redis_client:
        return
    
    key = f"prompt_cache:{tenant_id}:{get_prompt_hash(prompt)}"
    try:
        redis_client.setex(key, ttl, response)
        logger.debug(f"prompt_cache_saved: tenant={tenant_id}")
    except Exception as e:
        logger.warning(f"prompt_cache_save_failed: {e}")
