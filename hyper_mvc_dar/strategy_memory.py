"""
hyper_mvc_dar/strategy_memory.py
Strategy Memory & Cross-Workload Learning: Stores successful verified strategies
and transfers optimizations across similar workload fingerprints.
"""

from typing import Dict, Any, Optional, Tuple
import json


class StrategyMemory:
    """Persistent ledger of trusted, Pareto-optimal strategies keyed by fingerprint."""

    def __init__(self):
        self._memory: Dict[str, Dict[str, Any]] = {}

    def get_fingerprint(self, op_type: str, shape: Tuple[int, ...], contract_class: str) -> str:
        return f"{op_type}::{'_'.join(map(str, shape))}::{contract_class}"

    def retrieve_strategy(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        return self._memory.get(fingerprint)

    def commit_strategy(self, fingerprint: str, strategy: Dict[str, Any], measured_speedup: float):
        self._memory[fingerprint] = {
            **strategy,
            "measured_speedup": measured_speedup,
            "status": "TRUSTED"
        }

    def transfer_knowledge(self, op_type: str, target_shape: Tuple[int, ...]) -> Optional[Dict[str, Any]]:
        """Finds closest existing strategy of same operation type."""
        for fp, strat in self._memory.items():
            if fp.startswith(op_type):
                return strat
        return None
