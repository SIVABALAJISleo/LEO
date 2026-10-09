"""
hyper/failure_knowledge/failure_memory.py
=========================================
Failure Knowledge Base for HYPER-GODMODE.
Implements Section 24 (Failure is Data) of the HYPER-GODMODE specification:
«Never simply delete failed candidates. Store failure type, counterexample, bottleneck, and learned constraints.
 Use failures to guide and constrain future pathway searches.»
"""

from __future__ import annotations
import enum
import json
import os
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FailureCategory(str, enum.Enum):
    CORRECTNESS_FAILURE = "CORRECTNESS_FAILURE"
    PERFORMANCE_FAILURE = "PERFORMANCE_FAILURE"
    MEMORY_PRESSURE_FAILURE = "MEMORY_PRESSURE_FAILURE"
    THERMAL_THROTTLING_FAILURE = "THERMAL_THROTTLING_FAILURE"
    SYNCHRONIZATION_DEADLOCK = "SYNCHRONIZATION_DEADLOCK"
    GENERALIZATION_COLLAPSE = "GENERALIZATION_COLLAPSE"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"


class GodmodeFailureRecord(BaseModel):
    failure_id: str
    workload_name: str
    pathway_id: str
    category: FailureCategory
    failed_transformation: str
    counterexample_summary: str
    bottleneck_description: str
    learned_constraint: str
    timestamp: float = Field(default_factory=time.time)


class FailureKnowledgeBase:
    """
    Persistent memory repository for failed attempts, enabling negative learning and search pruning.
    """

    def __init__(self, storage_path: str = "reports/godmode_failure_knowledge.json") -> None:
        self.storage_path = storage_path
        self.records: Dict[str, GodmodeFailureRecord] = {}
        self.learned_constraints: List[str] = []
        self._load()

    def record_failure(
        self,
        workload_name: str,
        pathway_id: str,
        category: FailureCategory,
        failed_transformation: str,
        counterexample_summary: str,
        bottleneck_description: str,
        learned_constraint: str,
    ) -> GodmodeFailureRecord:
        rec = GodmodeFailureRecord(
            failure_id=f"FAIL_{int(time.time()*1000)%1000000}",
            workload_name=workload_name,
            pathway_id=pathway_id,
            category=category,
            failed_transformation=failed_transformation,
            counterexample_summary=counterexample_summary,
            bottleneck_description=bottleneck_description,
            learned_constraint=learned_constraint,
        )
        self.records[rec.failure_id] = rec
        if learned_constraint not in self.learned_constraints:
            self.learned_constraints.append(learned_constraint)
        self._save()
        return rec

    def is_transformation_forbidden(self, workload_name: str, transformation: str) -> bool:
        """
        Checks if a transformation was previously proven to fail correctness for this workload.
        """
        for r in self.records.values():
            if r.workload_name == workload_name and r.failed_transformation == transformation:
                if r.category in [FailureCategory.CORRECTNESS_FAILURE, FailureCategory.CONTRACT_VIOLATION]:
                    return True
        return False

    def query_constraints_for_workload(self, workload_name: str) -> List[str]:
        return [
            r.learned_constraint
            for r in self.records.values()
            if r.workload_name == workload_name
        ]

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "failures": [r.model_dump() for r in self.records.values()],
                "learned_constraints": self.learned_constraints,
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("failures", []):
                        rec = GodmodeFailureRecord(**item)
                        self.records[rec.failure_id] = rec
                    self.learned_constraints = data.get("learned_constraints", [])
            except Exception:
                pass
