"""
hyper_x/counterexample_registry.py
==================================
Section 29: Counterexample Learning Registry.
Stores all falsification and failure events as structured learning signals.
Prevents the search engines from repeating transformations already disproven
under identical structural or numerical conditions.
"""

from __future__ import annotations
import enum
import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set


class FailureClass(str, enum.Enum):
    INSUFFICIENT_STRUCTURE = "insufficient_structure"
    NUMERICAL_INSTABILITY = "numerical_instability"
    CANDIDATE_SLOWER = "candidate_slower"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    TRANSFER_BOUND = "transfer_bound"
    THERMAL_BOUND = "thermal_bound"
    EQUIVALENCE_FAILURE = "equivalence_failure"
    CONTRACT_FAILURE = "contract_failure"
    GENERALIZATION_FAILURE = "generalization_failure"
    UNSUPPORTED_BACKEND = "unsupported_backend"
    ALGORITHM_SEARCH_FAILURE = "algorithm_search_failure"


@dataclass
class CounterexampleRecord:
    record_id: str
    workload_class: str
    failure_mode: FailureClass
    candidate_id: str
    transformation_name: str
    input_hash: str
    expected_output_hash: str
    actual_output_hash: str
    numerical_error: float
    hardware: str
    environment: str
    reproducibility_command: str
    structural_conditions: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["failure_mode"] = self.failure_mode.value
        return d


class CounterexampleRegistry:
    """
    Central repository of disproven hypotheses and counterexamples.
    Enforces the rule: 'Do not repeatedly attempt a transformation
    already disproven for the same structural conditions.'
    """

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path
        self._records: List[CounterexampleRecord] = []
        # Key: (transformation_name, workload_class) -> List[conditions]
        self._disproven_rules: Dict[str, List[Dict[str, Any]]] = {}
        if persistence_path and os.path.exists(persistence_path):
            self.load(persistence_path)

    def record_counterexample(
        self,
        workload_class: str,
        failure_mode: FailureClass,
        candidate_id: str,
        transformation_name: str,
        input_hash: str,
        expected_output_hash: str,
        actual_output_hash: str,
        numerical_error: float,
        hardware: str,
        environment: str,
        reproducibility_command: str,
        structural_conditions: Optional[Dict[str, Any]] = None,
        notes: str = "",
    ) -> CounterexampleRecord:
        record_id = hashlib.sha256(
            f"{candidate_id}:{transformation_name}:{input_hash}:{failure_mode.value}:{time.time()}".encode("utf-8")
        ).hexdigest()[:16]

        record = CounterexampleRecord(
            record_id=record_id,
            workload_class=workload_class,
            failure_mode=failure_mode,
            candidate_id=candidate_id,
            transformation_name=transformation_name,
            input_hash=input_hash,
            expected_output_hash=expected_output_hash,
            actual_output_hash=actual_output_hash,
            numerical_error=float(numerical_error),
            hardware=hardware,
            environment=environment,
            reproducibility_command=reproducibility_command,
            structural_conditions=structural_conditions or {},
            notes=notes,
        )
        self._records.append(record)

        rule_key = f"{transformation_name}::{workload_class}"
        if rule_key not in self._disproven_rules:
            self._disproven_rules[rule_key] = []
        self._disproven_rules[rule_key].append(record.structural_conditions)

        if self.persistence_path:
            self.save(self.persistence_path)

        return record

    def is_transformation_disproven(
        self,
        transformation_name: str,
        workload_class: str,
        structural_conditions: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Checks whether the candidate transformation has already failed
        under compatible structural conditions.
        """
        rule_key = f"{transformation_name}::{workload_class}"
        if rule_key not in self._disproven_rules:
            return False

        if not structural_conditions:
            # If no specific conditions provided, any failure under this workload marks it disproven
            return len(self._disproven_rules[rule_key]) > 0

        # Check if conditions match any past failed run
        for failed_cond in self._disproven_rules[rule_key]:
            match = True
            for k, v in failed_cond.items():
                if k in structural_conditions and structural_conditions[k] != v:
                    match = False
                    break
            if match and len(failed_cond) > 0:
                return True

        return False

    def query_failures(
        self,
        workload_class: Optional[str] = None,
        failure_mode: Optional[FailureClass] = None,
    ) -> List[CounterexampleRecord]:
        results = self._records
        if workload_class:
            results = [r for r in results if r.workload_class == workload_class]
        if failure_mode:
            results = [r for r in results if r.failure_mode == failure_mode]
        return results

    def get_summary(self) -> Dict[str, Any]:
        counts_by_mode: Dict[str, int] = {}
        for r in self._records:
            counts_by_mode[r.failure_mode.value] = counts_by_mode.get(r.failure_mode.value, 0) + 1
        return {
            "total_counterexamples": len(self._records),
            "disproven_rules_count": len(self._disproven_rules),
            "breakdown_by_mode": counts_by_mode,
        }

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "records": [r.to_dict() for r in self._records],
            "disproven_rules": self._disproven_rules,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._records = []
        for rd in data.get("records", []):
            fm = FailureClass(rd["failure_mode"])
            rec = CounterexampleRecord(
                record_id=rd["record_id"],
                workload_class=rd["workload_class"],
                failure_mode=fm,
                candidate_id=rd["candidate_id"],
                transformation_name=rd["transformation_name"],
                input_hash=rd["input_hash"],
                expected_output_hash=rd["expected_output_hash"],
                actual_output_hash=rd["actual_output_hash"],
                numerical_error=rd["numerical_error"],
                hardware=rd["hardware"],
                environment=rd["environment"],
                reproducibility_command=rd["reproducibility_command"],
                structural_conditions=rd.get("structural_conditions", {}),
                notes=rd.get("notes", ""),
                timestamp=rd.get("timestamp", time.time()),
            )
            self._records.append(rec)
        self._disproven_rules = data.get("disproven_rules", {})
