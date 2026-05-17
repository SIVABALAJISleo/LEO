import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("HyperCore.ContextThreadManager")

class ContextThreadManager:
    """
    HyperCore PHASE 3 — Context Thread Manager
    
    Manages parallel multitasking workflow threads for enterprise workers.
    Detects semantic switches and enables zero-cost warm-context resumption.
    """
    def __init__(self):
        # Maps thread_id -> thread_state dictionary
        self.threads: Dict[str, Dict[str, Any]] = {}
        self.active_thread_id: Optional[str] = None
        
    def create_thread(self, thread_id: str, domain: str, initial_query: str):
        self.threads[thread_id] = {
            "thread_id": thread_id,
            "domain": domain,
            "queries": [initial_query],
            "last_accessed": time.time(),
            "state": "ACTIVE",
            "history": []
        }
        self.active_thread_id = thread_id
        logger.info(f"Created thread '{thread_id}' inside domain '{domain}'")
        
    def detect_thread_switch(self, query: str) -> Optional[str]:
        """
        Statically checks if the query corresponds to a semantic shift to another thread.
        Matches domains (e.g. legal, tax, SLA) to keep context isolated.
        """
        query_clean = query.lower()
        
        # Rule-based switch check for simulation
        for thread_id, data in self.threads.items():
            if data["domain"] == "legal" and any(w in query_clean for w in ["contract", "guideline", "liability"]):
                return thread_id
            if data["domain"] == "tax" and any(w in query_clean for w in ["invoice", "ledger", "tax", "reconcile"]):
                return thread_id
                
        return None
        
    def switch_to_thread(self, thread_id: str):
        if thread_id in self.threads:
            self.active_thread_id = thread_id
            self.threads[thread_id]["last_accessed"] = time.time()
            logger.info(f"Switched active thread to '{thread_id}' (Warm Context Resumed)")
            
    def get_active_thread(self) -> Optional[Dict[str, Any]]:
        if self.active_thread_id:
            return self.threads[self.active_thread_id]
        return None
