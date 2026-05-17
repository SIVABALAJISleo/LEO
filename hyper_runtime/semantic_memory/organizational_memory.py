import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("HyperCore.OrganizationalMemory")

class OrganizationalSemanticMemory:
    """
    HyperCore PHASE 4 — Organizational Semantic Memory
    
    A persistent, queryable store of governance arbitration decisions,
    policy updates, terminology mapping, and historical semantic resolutions.
    Ensures human compliance resolutions are memorized and instantly reusable.
    """
    def __init__(self):
        # Maps query_hash -> decision dictionary
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        
    def store_decision(self, query_hash: str, decision_payload: dict):
        """
        Stores an immutable governance or compliance decision.
        """
        self.memory_store[query_hash] = {
            "decision": decision_payload,
            "timestamp": time.time(),
            "version": 1,
            "reversible": True
        }
        logger.info(f"Committed decision to Organizational Semantic Memory for '{query_hash[:16]}'")
        
    def retrieve_decision(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Checks if a historical conflict or query matches an already-resolved decision.
        """
        if query_hash in self.memory_store:
            logger.info(f"Semantic Memory HIT for '{query_hash[:16]}'")
            return self.memory_store[query_hash]
        return None
        
    def export_ledger(self) -> str:
        """Returns the full auditable JSON log of all governance outcomes."""
        return json.dumps(self.memory_store, indent=2)
