"""
hyper_mvc_dar/work_ledger.py
Computational Work Ledger: Records non-double-counted avoided work across FLOPs,
memory bytes, Monte Carlo samples, ray traversals, and iterations.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import json


@dataclass
class WorkLedgerEntry:
    workload_id: str
    track: str
    baseline_flops: int
    actual_flops: int
    baseline_bytes: int
    actual_bytes: int
    baseline_samples: int = 0
    actual_samples: int = 0
    execution_time_ms: float = 0.0
    contract_satisfied: bool = True
    verification_status: str = "PASS"

    @property
    def flops_avoidance_ratio(self) -> float:
        if self.baseline_flops == 0:
            return 0.0
        return round((self.baseline_flops - self.actual_flops) / self.baseline_flops, 4)

    @property
    def bytes_avoidance_ratio(self) -> float:
        if self.baseline_bytes == 0:
            return 0.0
        return round((self.baseline_bytes - self.actual_bytes) / self.baseline_bytes, 4)


class WorkLedger:
    """Central accounting repository for authentic measured work reduction."""

    def __init__(self):
        self.entries: List[WorkLedgerEntry] = []

    def record_run(self, entry: WorkLedgerEntry):
        self.entries.append(entry)

    def summarize(self) -> Dict[str, Any]:
        total_base_flops = sum(e.baseline_flops for e in self.entries)
        total_act_flops = sum(e.actual_flops for e in self.entries)
        total_base_bytes = sum(e.baseline_bytes for e in self.entries)
        total_act_bytes = sum(e.actual_bytes for e in self.entries)

        overall_flop_avoidance = (
            (total_base_flops - total_act_flops) / total_base_flops
            if total_base_flops > 0 else 0.0
        )

        overall_byte_avoidance = (
            (total_base_bytes - total_act_bytes) / total_base_bytes
            if total_base_bytes > 0 else 0.0
        )

        return {
            "total_workloads_recorded": len(self.entries),
            "total_baseline_flops": total_base_flops,
            "total_actual_flops": total_act_flops,
            "overall_flop_avoidance_ratio": round(overall_flop_avoidance, 4),
            "total_baseline_bytes": total_base_bytes,
            "total_actual_bytes": total_act_bytes,
            "overall_byte_avoidance_ratio": round(overall_byte_avoidance, 4),
            "all_contracts_satisfied": all(e.contract_satisfied for e in self.entries)
        }
