"""
hyper/escape_engine/learning/pathway_history.py
===============================================
VAEE Section 21: Persistent Search Memory & Pathway History.

Stores structured experiment records in JSONL format, allowing previous successful
pathways to serve as starting points for future searches.
"""

from __future__ import annotations

import dataclasses
import json
import os
import time
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class PathwayHistoryRecord:
    experiment_id: str
    workload_type: str
    contract_id: str
    pathway_id: str
    parent_id: Optional[str]
    transformation_chain: List[str]
    structural_hash: str
    hardware: str
    runtime_ms: float
    verification_status: str
    speedup_vs_baseline: float
    outcome: str                      # SUCCESS | FAILURE | UNKNOWN | BARRIER
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class PathwayHistoryStore:
    """Persistent storage for pathway exploration history."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "reports", "vaee_pathway_history.jsonl"
        )
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.records: List[PathwayHistoryRecord] = []

    def record(self, record: PathwayHistoryRecord) -> None:
        self.records.append(record)
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict()) + "\n")
        except Exception:
            pass

    def get_successful_pathways(self, workload_type: str) -> List[PathwayHistoryRecord]:
        return [r for r in self.records if r.workload_type == workload_type and r.outcome == "SUCCESS"]
