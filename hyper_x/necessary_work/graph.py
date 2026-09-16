"""
hyper_x/necessary_work/graph.py
===============================
HYPER-Ω Necessary-Work Graph:
Represents fine-grained operations, tensors, memory transfers, and synchronizations.
Enforces strict node classification:
    REQUIRED
    REUSABLE
    INCREMENTAL
    ELIMINABLE
    CONTRACT_OPTIONAL
    PREDICTIVE
    APPROXIMATE
    UNKNOWN

UNKNOWN work must NOT be eliminated automatically (fail-closed).
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


class WorkNodeState(str, enum.Enum):
    REQUIRED = "REQUIRED"
    REUSABLE = "REUSABLE"
    INCREMENTAL = "INCREMENTAL"
    ELIMINABLE = "ELIMINABLE"
    CONTRACT_OPTIONAL = "CONTRACT_OPTIONAL"
    PREDICTIVE = "PREDICTIVE"
    APPROXIMATE = "APPROXIMATE"
    UNKNOWN = "UNKNOWN"

WorkState = WorkNodeState


class WorkNodeType(str, enum.Enum):
    OPERATION = "OPERATION"
    TENSOR = "TENSOR"
    MEMORY_TRANSFER = "MEMORY_TRANSFER"
    SYNCHRONIZATION = "SYNCHRONIZATION"
    KERNEL = "KERNEL"
    STATE_UPDATE = "STATE_UPDATE"
    OBSERVABLE = "OBSERVABLE"


@dataclass
class WorkGraphNode:
    node_id: str
    node_type: WorkNodeType
    state: WorkNodeState = WorkNodeState.UNKNOWN  # Default fail-closed
    cost_flops: float = 0.0
    memory_bytes: float = 0.0
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    elimination_justification: str = ""
    reproducibility_evidence: str = ""


class NecessaryWorkGraph:
    """
    Directed Acyclic Graph representing computational necessity.
    Tracks work elimination mathematically with proof justifications.
    """

    def __init__(self):
        self.nodes: Dict[str, WorkGraphNode] = {}

    def add_node(
        self,
        node_id: str,
        node_type: WorkNodeType,
        cost_flops: float = 0.0,
        memory_bytes: float = 0.0,
        inputs: Optional[List[str]] = None,
        state: WorkNodeState = WorkNodeState.UNKNOWN,
    ) -> WorkGraphNode:
        node = WorkGraphNode(
            node_id=node_id,
            node_type=node_type,
            state=state,
            cost_flops=cost_flops,
            memory_bytes=memory_bytes,
            inputs=inputs or [],
        )
        self.nodes[node_id] = node
        return node

    def classify_node(self, node_id: str, new_state: WorkNodeState, justification: str):
        if node_id in self.nodes:
            self.nodes[node_id].state = new_state
            self.nodes[node_id].elimination_justification = justification

    def compute_work_summary(self) -> Dict[str, float]:
        """
        Calculates reference total work vs candidate verified necessary work.
        """
        total_nominal_flops = sum(n.cost_flops for n in self.nodes.values())
        necessary_flops = sum(
            n.cost_flops for n in self.nodes.values()
            if n.state in [WorkNodeState.REQUIRED, WorkNodeState.UNKNOWN]
        )
        eliminated_flops = sum(
            n.cost_flops for n in self.nodes.values()
            if n.state in [WorkNodeState.ELIMINABLE, WorkNodeState.CONTRACT_OPTIONAL]
        )
        reused_flops = sum(
            n.cost_flops for n in self.nodes.values()
            if n.state in [WorkNodeState.REUSABLE, WorkNodeState.INCREMENTAL]
        )

        elimination_ratio = eliminated_flops / max(1.0, total_nominal_flops)
        reuse_ratio = reused_flops / max(1.0, total_nominal_flops)
        verified_work_elimination = (eliminated_flops + reused_flops) / max(1.0, total_nominal_flops)

        return {
            "total_nominal_flops": total_nominal_flops,
            "necessary_flops": necessary_flops,
            "eliminated_flops": eliminated_flops,
            "reused_flops": reused_flops,
            "elimination_ratio": round(elimination_ratio, 4),
            "reuse_ratio": round(reuse_ratio, 4),
            "verified_work_elimination": round(verified_work_elimination, 4),
        }
