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

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import psutil

class MemoryGuardMiddleware(BaseHTTPMiddleware):
    """
    Proactive Load Shedder:
    Returns 503 if system memory usage exceeds 90%.
    """
    def __init__(self, app, max_mem_percent: float = 90.0):
        super().__init__(app)
        self.max_mem_percent = max_mem_percent

    async def dispatch(self, request, call_next):
        mem = psutil.virtual_memory().percent
        if mem > self.max_mem_percent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "overloaded",
                    "detail": "System memory pressure high. Shedding load.",
                    "mem_percent": mem
                }
            )
        return await call_next(request)
