import logging
import json
from typing import List, Dict, Any, Optional
from backend.core.middleware import redis_client

logger = logging.getLogger(__name__)

class ConversationMemory:
    def __init__(self, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def _get_key(self, session_id: str, tenant_id: str) -> str:
        return f"memory:{tenant_id}:{session_id}"

    def add_message(self, session_id: str, tenant_id: str, role: str, content: str):
        """Adds a message to the session memory."""
        if not self.redis:
            return
        
        key = self._get_key(session_id, tenant_id)
        message = {"role": role, "content": content}
        try:
            # We store as a JSON list in Redis
            history = self.get_history(session_id, tenant_id)
            history.append(message)
            # Keep only last 10 messages for context window management
            history = history[-10:]
            self.redis.setex(key, self.ttl, json.dumps(history))
            logger.debug(f"memory_updated: session={session_id} tenant={tenant_id}")
        except Exception as e:
            logger.warning(f"memory_update_failed: {e}")

    def get_history(self, session_id: str, tenant_id: str) -> List[Dict[str, str]]:
        """Retrieves history for the session."""
        if not self.redis:
            return []
        
        key = self._get_key(session_id, tenant_id)
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"memory_retrieval_failed: {e}")
        return []

    def clear(self, session_id: str, tenant_id: str):
        """Clears memory for a session."""
        if not self.redis:
            return
        key = self._get_key(session_id, tenant_id)
        self.redis.delete(key)

# Global instance
global_memory = ConversationMemory()
