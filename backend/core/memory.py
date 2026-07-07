import sqlite3
from backend.core.db_utils import get_concurrent_db_connection
import logging
import json
from datetime import datetime
from typing import List, Dict
from backend.core.middleware import redis_client

logger = logging.getLogger(__name__)

class ConversationMemory:
    def __init__(self, ttl: int = 3600, db_path: str = "memory_fallback.db"):
        self.redis = redis_client
        self.ttl = ttl
        self.db_path = db_path
        self._init_sqlite()

    def _init_sqlite(self):
        """Initializes local SQLite database for persistent fallback."""
        try:
            conn = get_concurrent_db_connection(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT,
                    session_id TEXT,
                    history TEXT,
                    updated_at TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"sqlite_init_failed: {e}")

    def _get_key(self, session_id: str, tenant_id: str) -> str:
        return f"memory:{tenant_id}:{session_id}"

    def add_message(self, session_id: str, tenant_id: str, role: str, content: str):
        """Adds a message to the session memory with Redis + SQLite persistence."""
        key = self._get_key(session_id, tenant_id)
        message = {"role": role, "content": content}
        
        # 1. Update in-memory/Redis cache
        history = self.get_history(session_id, tenant_id)
        history.append(message)
        history = history[-10:]
        serialized = json.dumps(history)
        
        if self.redis and hasattr(self.redis, 'ping') and self.redis.ping():
            try:
                self.redis.setex(key, self.ttl, serialized)
            except Exception as e:
                logger.warning(f"redis_memory_update_failed: {e}")
        
        # 2. Update persistent SQLite fallback
        try:
            conn = get_concurrent_db_connection(self.db_path)
            conn.execute("""
                INSERT OR REPLACE INTO conversation_memory (id, tenant_id, session_id, history, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (key, tenant_id, session_id, serialized, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"sqlite_memory_update_failed: {e}")

    def get_history(self, session_id: str, tenant_id: str) -> List[Dict[str, str]]:
        """Retrieves history from Redis (fast) or SQLite (persistent fallback)."""
        key = self._get_key(session_id, tenant_id)
        
        # 1. Try Redis first
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    return json.loads(data) # type: ignore
            except Exception: # nosec B110
                pass
        
        # 2. Fallback to SQLite
        try:
            conn = get_concurrent_db_connection(self.db_path)
            cursor = conn.execute("SELECT history FROM conversation_memory WHERE id = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
        except Exception as e:
            logger.warning(f"sqlite_memory_retrieval_failed: {e}")
            
        return []

    def clear(self, session_id: str, tenant_id: str):
        """Clears memory from both stores."""
        key = self._get_key(session_id, tenant_id)
        if self.redis:
            try:
                self.redis.delete(key)
            except: # nosec B110
                pass
            
        try:
            conn = get_concurrent_db_connection(self.db_path)
            conn.execute("DELETE FROM conversation_memory WHERE id = ?", (key,))
            conn.commit()
            conn.close()
        except: # nosec B110
            pass

global_memory = ConversationMemory()
