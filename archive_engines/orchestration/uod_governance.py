import json
import os
import datetime
from typing import Dict, Any, List
from archive_engines.orchestration.ontology import global_registry

class UOD_Governance:
    """
    Module 8: GOVERNANCE
    Tracks ontology versions and schema changes.
    """
    def __init__(self, history_file: str = "./data/ontology_history.json"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return []

    def checkpoint(self, version: str, author: str = "system"):
        """Save a snapshot of the current ontology."""
        snapshot = {
            "version": version,
            "timestamp": datetime.datetime.now().isoformat(),
            "author": author,
            "properties": [vars(p) for p in global_registry.list_properties()]
        }
        self.history.append(snapshot)
        
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)
        
        return snapshot

    def get_version_history(self):
        return self.history

global_uod_governance = UOD_Governance()
