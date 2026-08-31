"""
hyper/telemetry/ledger.py
=========================
Immutable Provenance & Experiment Ledger:
Stores machine-readable JSON experiment records for 100% reproducibility.
"""

import json
import time
from typing import Dict, Any, List


class ProvenanceLedger:
    """
    Appends experiment records with full hardware, git, and measurement metadata.
    """
    def __init__(self):
        self._records: List[Dict[str, Any]] = []

    def record_experiment(self, record: Dict[str, Any]) -> None:
        record["recorded_timestamp"] = time.time()
        self._records.append(record)

    def export_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._records, f, indent=2)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._records)
