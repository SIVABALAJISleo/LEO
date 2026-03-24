import os
import logging

logger = logging.getLogger(__name__)

# Fault-tolerant Redis Client Mock/Connection
redis_client = None
try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Use a short timeout for the connection check
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    r = redis.Redis(host=host, port=port, socket_connect_timeout=1)
    r.ping()
    redis_client = r
    logger.info("Connected to Redis successfully.")
except Exception as e:
    logger.warning(f"Redis not available, using in-memory fallback. Error: {e}")
    
    class SQLiteFallback:
        """Persistent fallback. Survives server restarts unlike FakeRedis."""
        def __init__(self, db_path="/tmp/hyper_cache.db"):
            import sqlite3, json, time
            self._db = db_path
            self._sqlite3 = sqlite3
            self._json = json
            self._time = time
            with sqlite3.connect(db_path) as c:
                c.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)")
                c.commit()

        def set(self, key, value, ex=None):
            import sqlite3, json, time
            exp = (time.time() + ex) if ex else None
            with sqlite3.connect(self._db) as c:
                c.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?)", (key, json.dumps(value), exp))
            return True

        def setnx(self, key, value):
            if self.get(key) is not None:
                return False
            self.set(key, value)
            return True

        def get(self, key):
            import sqlite3, json, time
            with sqlite3.connect(self._db) as c:
                row = c.execute("SELECT value, expires_at FROM cache WHERE key=?", (key,)).fetchone()
            if not row: return None
            val, exp = row
            if exp and time.time() > exp:
                return None
            return json.loads(val)

        def expire(self, key, seconds):
            import sqlite3, time
            with sqlite3.connect(self._db) as c:
                c.execute("UPDATE cache SET expires_at=? WHERE key=?", (time.time()+seconds, key))
            return True

        def ping(self): return True

    redis_client = SQLiteFallback()

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
