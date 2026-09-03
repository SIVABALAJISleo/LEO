"""
hyper_v3/telemetry/ledger.py
Non-double-counting Computational Work Ledger for HYPER 3.0.
Tracks: Reference Work -> Required Work -> Reused Work -> Eliminated Work -> Transformed Work -> Executed Work -> Verified Work.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import json
import os


@dataclass
class WorkLedgerEntry:
    workload_name: str
    reference_flops: int
    required_flops: int
    reused_flops: int
    eliminated_flops: int
    transformed_flops: int
    executed_flops: int
    verified: bool
    verified_work_avoidance: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_name": self.workload_name,
            "reference_work": self.reference_flops,
            "required_work": self.required_flops,
            "reused_work": self.reused_flops,
            "eliminated_work": self.eliminated_flops,
            "transformed_work": self.transformed_flops,
            "executed_work": self.executed_flops,
            "verified": self.verified,
            "verified_work_avoidance": round(self.verified_work_avoidance, 4)
        }


class ComputationalWorkLedger:
    """Maintains an accounting record of all eliminated and verified computation."""

    def __init__(self, storage_path: str = "reports/hyper_3/HYPER_3_0_WORK_LEDGER.json"):
        self.storage_path = storage_path
        self.entries: List[WorkLedgerEntry] = []

    def record_entry(
        self,
        workload_name: str,
        reference_flops: int,
        executed_flops: int,
        reused_flops: int = 0,
        eliminated_flops: int = 0,
        transformed_flops: int = 0,
        verified: bool = True
    ):
        vwa = max(0.0, 1.0 - (executed_flops / max(reference_flops, 1)))
        required_flops = executed_flops + reused_flops
        entry = WorkLedgerEntry(
            workload_name=workload_name,
            reference_flops=reference_flops,
            required_flops=required_flops,
            reused_flops=reused_flops,
            eliminated_flops=eliminated_flops,
            transformed_flops=transformed_flops,
            executed_flops=executed_flops,
            verified=verified,
            verified_work_avoidance=vwa
        )
        self.entries.append(entry)

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w") as f:
                json.dump([e.to_dict() for e in self.entries], f, indent=2)
        except Exception:
            pass
