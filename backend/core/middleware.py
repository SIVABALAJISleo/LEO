import os
import logging

logger = logging.getLogger(__name__)

# Fault-tolerant Redis Client Mock/Connection
try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Ping to check connection
    redis_client.ping()
    logger.info("Connected to Redis successfully.")
except (ImportError, Exception) as e:
    logger.warning(f"Redis not available, using in-memory fallback. Error: {e}")
    
    class FakeRedis:
        def __init__(self):
            self._storage = {}
        
        def set(self, key, value, ex=None):
            self._storage[key] = value
            return True
        
        def setnx(self, key, value):
            if key in self._storage:
                return False
            self._storage[key] = value
            return True
            
        def get(self, key):
            return self._storage.get(key)
            
        def expire(self, key, seconds):
            return True
            
        def ping(self):
            return True

    redis_client = FakeRedis()
