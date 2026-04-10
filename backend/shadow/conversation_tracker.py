import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ConversationTracker:
    """
    Tracks session state to provide context for shadow predictions.
    """
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def track(self, session_id: str, query: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "query": query,
            "timestamp": time.time()
        })
        
        # Max history for prediction depth
        if len(self.sessions[session_id]) > 5:
            self.sessions[session_id].pop(0)

global_tracker = ConversationTracker()
