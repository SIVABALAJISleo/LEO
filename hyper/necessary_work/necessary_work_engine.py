"""
Necessary-Work Engine for LEO/HYPER Ω.
Formally classifies every workload operation into necessity categories:
- REQUIRED
- CONDITIONAL
- REDUNDANT
- REUSABLE
- INCREMENTAL
- PREDICTABLE
- RECONSTRUCTABLE
- ELIMINABLE
- UNKNOWN

Calculates:
- reference_work
- necessary_work_estimate
- executed_work
- reused_work
- eliminated_work
- speculative_work
- verification_work

Core Objective: Minimize executed_work subject to contract == PASS.
"""

from __future__ import annotations

import enum
import dataclasses
from typing import Any, Dict, List, Optional
import numpy as np

from contracts.contract_ir import ContractIR, ExactnessClass
from hyper.work_dag.work_graph import WorkGraph, WorkNode


class NecessityClass(enum.Enum):
    REQUIRED          = "REQUIRED"
    CONDITIONAL       = "CONDITIONAL"
    REDUNDANT         = "REDUNDANT"
    REUSABLE          = "REUSABLE"
    INCREMENTAL       = "INCREMENTAL"
    PREDICTABLE       = "PREDICTABLE"
    RECONSTRUCTABLE   = "RECONSTRUCTABLE"
    ELIMINABLE        = "ELIMINABLE"
    UNKNOWN           = "UNKNOWN"


@dataclasses.dataclass
class NecessaryWorkLedger:
    reference_work_flops: float = 0.0
    necessary_work_estimate_flops: float = 0.0
    executed_work_flops: float = 0.0
    reused_work_flops: float = 0.0
    eliminated_work_flops: float = 0.0
    speculative_work_flops: float = 0.0
    verification_work_flops: float = 0.0
    bytes_read: int = 0
    bytes_written: int = 0
    bytes_reused: int = 0
    bytes_eliminated: int = 0

    @property
    def work_reduction_ratio(self) -> float:
        if self.reference_work_flops <= 0:
            return 0.0
        return max(0.0, 1.0 - (self.executed_work_flops / self.reference_work_flops))

    @property
    def data_movement_reduction_ratio(self) -> float:
        total_ref_bytes = self.bytes_read + self.bytes_written + self.bytes_eliminated
        if total_ref_bytes <= 0:
            return 0.0
        return max(0.0, self.bytes_eliminated / total_ref_bytes)

    def summary(self) -> Dict[str, Any]:
        return {
            "reference_work_flops": self.reference_work_flops,
            "necessary_work_estimate_flops": self.necessary_work_estimate_flops,
            "executed_work_flops": self.executed_work_flops,
            "reused_work_flops": self.reused_work_flops,
            "eliminated_work_flops": self.eliminated_work_flops,
            "speculative_work_flops": self.speculative_work_flops,
            "verification_work_flops": self.verification_work_flops,
            "work_reduction_pct": round(self.work_reduction_ratio * 100.0, 2),
            "bytes_read": self.bytes_read,
            "bytes_written": self.bytes_written,
            "bytes_reused": self.bytes_reused,
            "bytes_eliminated": self.bytes_eliminated,
            "data_movement_reduction_pct": round(self.data_movement_reduction_ratio * 100.0, 2),
        }


class NecessaryWorkEngine:
    """
    Analyzes computational workloads against contracts to classify necessity
    and compute work minimization bounds.
    """

    def __init__(self) -> None:
        self.ledger = NecessaryWorkLedger()

    def classify_node(self, node: WorkNode, contract: ContractIR, in_cache: bool = False, is_incremental: bool = False) -> NecessityClass:
        """
        Classifies an individual node based on its structural properties and contract.
        """
        if node.is_dead:
            return NecessityClass.ELIMINABLE

        if node.contract_relevance == "REDUNDANT":
            return NecessityClass.REDUNDANT

        if in_cache:
            return NecessityClass.REUSABLE

        if is_incremental:
            return NecessityClass.INCREMENTAL

        # Check for predictable / reconstructable low-rank structures
        if contract.exactness.exactness_class != ExactnessClass.EXACT:
            if "svd" in node.operation or "low_rank" in node.operation:
                return NecessityClass.RECONSTRUCTABLE

        return NecessityClass.REQUIRED

    def analyze_graph(self, graph: WorkGraph, contract: ContractIR, cached_node_ids: Optional[set] = None) -> NecessaryWorkLedger:
        """
        Walks the WorkGraph, categorizing operations and populating the work ledger.
        """
        cached_ids = cached_node_ids or set()
        ledger = NecessaryWorkLedger()

        for node in graph.nodes.values():
            w = node.estimated_work_flops
            mem = node.memory_footprint_bytes
            ledger.reference_work_flops += w

            n_class = self.classify_node(node, contract, in_cache=(node.node_id in cached_ids))

            if n_class in (NecessityClass.ELIMINABLE, NecessityClass.REDUNDANT):
                ledger.eliminated_work_flops += w
                ledger.bytes_eliminated += mem
            elif n_class == NecessityClass.REUSABLE:
                ledger.reused_work_flops += w
                ledger.eliminated_work_flops += w
                ledger.bytes_reused += mem
                ledger.bytes_eliminated += mem
            elif n_class == NecessityClass.INCREMENTAL:
                # Delta takes fraction (e.g. 20%)
                exec_w = w * 0.20
                ledger.executed_work_flops += exec_w
                ledger.eliminated_work_flops += (w - exec_w)
                ledger.bytes_read += int(mem * 0.20)
                ledger.bytes_written += int(mem * 0.20)
                ledger.bytes_eliminated += int(mem * 0.80)
            elif n_class == NecessityClass.RECONSTRUCTABLE:
                # Low-rank factorization work
                exec_w = w * 0.35
                ledger.executed_work_flops += exec_w
                ledger.eliminated_work_flops += (w - exec_w)
                ledger.bytes_read += int(mem * 0.35)
                ledger.bytes_written += int(mem * 0.35)
                ledger.bytes_eliminated += int(mem * 0.65)
            else:
                # Required
                ledger.executed_work_flops += w
                ledger.bytes_read += mem
                ledger.bytes_written += mem

        ledger.necessary_work_estimate_flops = ledger.executed_work_flops
        self.ledger = ledger
        return ledger
