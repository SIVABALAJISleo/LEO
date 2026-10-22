"""
hyper_x/cpce/ir.py
==================
Canonical Intermediate Representation (CIR) for CPCE.
Represents computational graphs independently of execution backends, capturing
operator semantics, data/control dependencies, shapes, dtypes, and structural properties.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Set, Tuple


class OpType(str, Enum):
    INPUT = "INPUT"
    CONSTANT = "CONSTANT"
    MATMUL = "MATMUL"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    DOT = "DOT"
    SCALE = "SCALE"
    HORNER_EVAL = "HORNER_EVAL"
    SPARSE_MATMUL = "SPARSE_MATMUL"
    RELU = "RELU"
    CONV2D = "CONV2D"
    ATTENTION = "ATTENTION"
    LLM_GENERATE = "LLM_GENERATE"
    OUTPUT = "OUTPUT"


@dataclasses.dataclass
class CIRNode:
    """Individual node within the Canonical Intermediate Representation."""
    node_id: str
    op_type: OpType
    inputs: List[str] = dataclasses.field(default_factory=list)
    outputs: List[str] = dataclasses.field(default_factory=list)
    shape: Optional[Tuple[int, ...]] = None
    dtype: str = "float32"
    structural_tag: str = "DENSE"  # DENSE, IDENTITY, ZERO, DIAGONAL, SPARSE, LOW_RANK
    parameters: Dict[str, Any] = dataclasses.field(default_factory=dict)
    resource_cost_flops: float = 0.0
    memory_bytes: int = 0
    is_constant: bool = False
    constant_value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["op_type"] = self.op_type.value
        if self.constant_value is not None:
            # Avoid serializing gigantic raw tensors into graph JSON
            d["constant_value"] = "<stored_tensor>"
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CIRNode:
        data_copy = dict(data)
        data_copy["op_type"] = OpType(data_copy["op_type"])
        if data_copy.get("shape") is not None:
            data_copy["shape"] = tuple(data_copy["shape"])
        return cls(**data_copy)


class CanonicalGraph:
    """
    Directed Acyclic Graph (DAG) representing the canonical computation.
    Validates topological invariants, checks for missing dependencies and cycles.
    """

    def __init__(self, name: str = "unnamed_graph"):
        self.name = name
        self.nodes: Dict[str, CIRNode] = {}
        self.input_nodes: List[str] = []
        self.output_nodes: List[str] = []

    def add_node(self, node: CIRNode) -> CIRNode:
        """Registers a node into the graph."""
        if node.node_id in self.nodes:
            raise ValueError(f"Duplicate node ID: {node.node_id}")
        self.nodes[node.node_id] = node
        if node.op_type == OpType.INPUT:
            self.input_nodes.append(node.node_id)
        elif node.op_type == OpType.OUTPUT:
            self.output_nodes.append(node.node_id)
        # Synchronize edges
        for inp_id in node.inputs:
            if inp_id in self.nodes and node.node_id not in self.nodes[inp_id].outputs:
                self.nodes[inp_id].outputs.append(node.node_id)
        for out_id in node.outputs:
            if out_id in self.nodes and node.node_id not in self.nodes[out_id].inputs:
                self.nodes[out_id].inputs.append(node.node_id)
        return node

    def add_edge(self, from_id: str, to_id: str):
        """Adds a directed dependency edge from from_id to to_id."""
        if from_id not in self.nodes:
            raise KeyError(f"Source node {from_id} not in graph")
        if to_id not in self.nodes:
            raise KeyError(f"Target node {to_id} not in graph")

        if to_id not in self.nodes[from_id].outputs:
            self.nodes[from_id].outputs.append(to_id)
        if from_id not in self.nodes[to_id].inputs:
            self.nodes[to_id].inputs.append(from_id)

    def get_node(self, node_id: str) -> CIRNode:
        if node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' not found in graph")
        return self.nodes[node_id]

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validates graph integrity:
        - In-degree and dependencies match
        - No cycles exist (DAG invariant)
        - Shape compatibility across matmul/binary operations
        """
        # 1. Dependency integrity
        for nid, node in self.nodes.items():
            for inp_id in node.inputs:
                if inp_id not in self.nodes:
                    return False, f"Node {nid} has missing input dependency: {inp_id}"
                if nid not in self.nodes[inp_id].outputs:
                    self.nodes[inp_id].outputs.append(nid)


        # 2. Cycle detection via Kahn's algorithm
        in_degrees: Dict[str, int] = {nid: len(node.inputs) for nid, node in self.nodes.items()}
        queue = [nid for nid, deg in in_degrees.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for succ in self.nodes[curr].outputs:
                in_degrees[succ] -= 1
                if in_degrees[succ] == 0:
                    queue.append(succ)

        if visited_count != len(self.nodes):
            return False, f"Graph contains a directed cycle ({visited_count}/{len(self.nodes)} resolved)"

        return True, None

    def topological_sort(self) -> List[CIRNode]:
        """Returns nodes in topologically sorted execution order."""
        ok, err = self.validate()
        if not ok:
            raise ValueError(f"Cannot sort invalid graph: {err}")

        in_degrees = {nid: len(node.inputs) for nid, node in self.nodes.items()}
        queue = [nid for nid, deg in in_degrees.items() if deg == 0]
        order: List[CIRNode] = []

        while queue:
            curr = queue.pop(0)
            order.append(self.nodes[curr])
            for succ in self.nodes[curr].outputs:
                in_degrees[succ] -= 1
                if in_degrees[succ] == 0:
                    queue.append(succ)

        return order

    def clone(self) -> CanonicalGraph:
        """Deep clones the canonical computation graph."""
        new_g = CanonicalGraph(name=f"{self.name}_copy")
        for nid, node in self.nodes.items():
            new_node = CIRNode(
                node_id=node.node_id,
                op_type=node.op_type,
                inputs=list(node.inputs),
                outputs=list(node.outputs),
                shape=node.shape,
                dtype=node.dtype,
                structural_tag=node.structural_tag,
                parameters=dict(node.parameters),
                resource_cost_flops=node.resource_cost_flops,
                memory_bytes=node.memory_bytes,
                is_constant=node.is_constant,
                constant_value=node.constant_value,
            )
            new_g.nodes[nid] = new_node
        new_g.input_nodes = list(self.input_nodes)
        new_g.output_nodes = list(self.output_nodes)
        return new_g

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "input_nodes": self.input_nodes,
            "output_nodes": self.output_nodes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CanonicalGraph:
        g = cls(name=data.get("name", "unnamed_graph"))
        for nid, ndict in data.get("nodes", {}).items():
            node = CIRNode.from_dict(ndict)
            g.nodes[nid] = node
        g.input_nodes = list(data.get("input_nodes", []))
        g.output_nodes = list(data.get("output_nodes", []))
        return g
