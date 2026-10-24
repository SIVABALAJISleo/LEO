"""
hyper_phase_change/ir.py
========================
Canonical Intermediate Representation (CIR) for Phase-Change Computation.

Represents operations with explicit:
- Operator type, operand shapes, dtypes, and memory layout.
- Mathematical preconditions and invariant constraints.
- Structural properties (sparsity, diagonal, identity, constant).
- Provenance and rewrite lineage.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set
import numpy as np


class LayoutType(str, Enum):
    C_CONTIGUOUS = "C_CONTIGUOUS"
    F_CONTIGUOUS = "F_CONTIGUOUS"
    STRIDED = "STRIDED"
    SPARSE_CSR = "SPARSE_CSR"
    SCALAR = "SCALAR"


@dataclasses.dataclass
class IRNode:
    """Canonical IR node representing an atomic or fused computational operation."""
    node_id: str
    op_type: str
    input_names: List[str]
    input_shapes: Dict[str, Tuple[int, ...]]
    input_dtypes: Dict[str, str]
    output_shape: Tuple[int, ...]
    output_dtype: str
    layout: LayoutType = LayoutType.C_CONTIGUOUS
    preconditions: List[str] = dataclasses.field(default_factory=list)
    structural_tags: Set[str] = dataclasses.field(default_factory=set)
    rewrite_provenance: Optional[str] = None
    estimated_flops: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "op_type": self.op_type,
            "input_names": self.input_names,
            "input_shapes": {k: list(v) for k, v in self.input_shapes.items()},
            "input_dtypes": self.input_dtypes,
            "output_shape": list(self.output_shape),
            "output_dtype": self.output_dtype,
            "layout": self.layout.value,
            "preconditions": self.preconditions,
            "structural_tags": sorted(list(self.structural_tags)),
            "rewrite_provenance": self.rewrite_provenance,
            "estimated_flops": self.estimated_flops,
        }


@dataclasses.dataclass
class IRGraph:
    """Directed Acyclic Graph of Canonical IR nodes."""
    graph_id: str
    nodes: Dict[str, IRNode] = dataclasses.field(default_factory=dict)
    execution_order: List[str] = dataclasses.field(default_factory=list)

    def add_node(self, node: IRNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.execution_order:
            self.execution_order.append(node.node_id)

    def get_node(self, node_id: str) -> Optional[IRNode]:
        return self.nodes.get(node_id)

    def total_estimated_flops(self) -> float:
        return sum(n.estimated_flops for n in self.nodes.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": len(self.nodes),
            "execution_order": self.execution_order,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "total_estimated_flops": self.total_estimated_flops(),
        }
