"""
hyper/necessity/necessity_analyzer.py
=====================================
Computation Necessity Engine (Section 8):
Classifies every operation/region into Necessity Classes:
NECESSARY, REDUNDANT, REUSABLE, PREDICTABLE, APPROXIMABLE, COMPRESSIBLE,
REPLACEABLE, INVARIANT, OPTIONAL, UNKNOWN.
Builds a Necessity Map: (necessary_work, avoidable_work, uncertain_work).
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass, field
from hyper.ir.workload_ir import WorkloadIR, IROperation


class NecessityClass(str, Enum):
    NECESSARY = "NECESSARY"
    REDUNDANT = "REDUNDANT"
    REUSABLE = "REUSABLE"
    PREDICTABLE = "PREDICTABLE"
    APPROXIMABLE = "APPROXIMABLE"
    COMPRESSIBLE = "COMPRESSIBLE"
    REPLACEABLE = "REPLACEABLE"
    INVARIANT = "INVARIANT"
    OPTIONAL = "OPTIONAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class NecessityMap:
    necessary_ops: List[str] = field(default_factory=list)
    avoidable_ops: List[str] = field(default_factory=list)
    uncertain_ops: List[str] = field(default_factory=list)
    necessary_flops: int = 0
    avoidable_flops: int = 0
    uncertain_flops: int = 0
    elimination_potential_pct: float = 0.0


class NecessityAnalyzer:
    """
    Evaluates computational necessity before execution.
    """
    def __init__(self):
        pass

    def analyze_workload(self, ir: WorkloadIR) -> NecessityMap:
        n_map = NecessityMap()

        for op_id, op in ir.operations.items():
            cat = op.attributes.get("necessity_class", NecessityClass.NECESSARY)
            
            if cat in [NecessityClass.REDUNDANT, NecessityClass.REUSABLE, NecessityClass.PREDICTABLE, NecessityClass.APPROXIMABLE, NecessityClass.REPLACEABLE]:
                n_map.avoidable_ops.append(op_id)
                n_map.avoidable_flops += op.estimated_flops
            elif cat == NecessityClass.UNKNOWN:
                n_map.uncertain_ops.append(op_id)
                n_map.uncertain_flops += op.estimated_flops
            else:
                n_map.necessary_ops.append(op_id)
                n_map.necessary_flops += op.estimated_flops

        total = max(1, ir.total_baseline_flops)
        n_map.elimination_potential_pct = round((n_map.avoidable_flops / total) * 100.0, 2)
        return n_map
