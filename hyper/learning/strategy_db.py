"""
hyper/learning/strategy_db.py
=============================
Learning Strategy Database (Section 37):
Stores winning execution strategies indexed by (workload_signature, contract_signature).
Accelerates subsequent executions without bypassing verification.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class StrategyEntry:
    workload_signature: str
    contract_signature: str
    optimal_strategy: str
    target_device: str
    measured_speedup: float
    measured_cer: float


class StrategyDatabase:
    """
    Registry of verified optimal execution paths.
    """
    def __init__(self):
        self._table: Dict[str, StrategyEntry] = {}

    def _make_key(self, workload_sig: str, contract_sig: str) -> str:
        return f"{workload_sig}::{contract_sig}"

    def record(self, entry: StrategyEntry) -> None:
        key = self._make_key(entry.workload_signature, entry.contract_signature)
        self._table[key] = entry

    def query(self, workload_sig: str, contract_sig: str) -> Optional[StrategyEntry]:
        key = self._make_key(workload_sig, contract_sig)
        return self._table.get(key)
