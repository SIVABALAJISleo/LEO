"""
hyper_omega/ir/graph.py
Canonical Computational Intermediate Representation (IR).
Represents arbitrary workloads as a Directed Acyclic Graph (DAG) of nodes,
preserving operations, dependencies, constants, data types, and semantic hashes.
"""
from __future__ import annotations
import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class IROpType(str, Enum):
    INPUT = "INPUT"
    CONSTANT = "CONSTANT"
    MATMUL = "MATMUL"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    DOT = "DOT"
    CONV2D = "CONV2D"
    FFT = "FFT"
    IFFT = "IFFT"
    RELU = "RELU"
    REDUCE_SUM = "REDUCE_SUM"
    REDUCE_MAX = "REDUCE_MAX"
    ARGMAX = "ARGMAX"
    SLICE = "SLICE"
    SPARSE_MATMUL = "SPARSE_MATMUL"
    RANK1_UPDATE = "RANK1_UPDATE"
    OUTPUT = "OUTPUT"


class IRNode(BaseModel):
    node_id: str
    op_type: IROpType
    inputs: List[str] = Field(default_factory=list)
    shape: Optional[Tuple[int, ...]] = None
    dtype: str = "float64"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    is_dead: bool = False
    is_constant: bool = False
    constant_value_hash: Optional[str] = None


class ComputationalIR(BaseModel):
    """Canonical DAG representation of a computational workload."""
    ir_id: str
    nodes: Dict[str, IRNode] = Field(default_factory=dict)
    input_nodes: List[str] = Field(default_factory=list)
    output_nodes: List[str] = Field(default_factory=list)

    def add_node(self, node: IRNode) -> None:
        self.nodes[node.node_id] = node
        if node.op_type == IROpType.INPUT and node.node_id not in self.input_nodes:
            self.input_nodes.append(node.node_id)
        elif node.op_type == IROpType.OUTPUT and node.node_id not in self.output_nodes:
            self.output_nodes.append(node.node_id)

    def compute_ir_hash(self) -> str:
        """Computes a deterministic cryptographic hash of the computational graph topology and ops."""
        serialized = []
        for n_id in sorted(self.nodes.keys()):
            n = self.nodes[n_id]
            serialized.append(f"{n.node_id}:{n.op_type.value}:{','.join(n.inputs)}:{n.shape}:{n.dtype}")
        raw = "|".join(serialized)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_topological_sort(self) -> List[str]:
        """Returns topological ordering of node IDs."""
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(curr: str):
            visited.add(curr)
            for inp in self.nodes[curr].inputs:
                if inp in self.nodes and inp not in visited:
                    dfs(inp)
            order.append(curr)

        for out_id in self.output_nodes:
            if out_id in self.nodes and out_id not in visited:
                dfs(out_id)
        return order

    def count_operations(self) -> int:
        """Estimates raw arithmetic operations in the IR graph."""
        count = 0
        for node in self.nodes.values():
            if node.is_dead:
                continue
            if node.op_type == IROpType.MATMUL and node.shape and len(node.shape) >= 2:
                # 2 * M * N * K
                count += 2 * node.shape[0] * node.shape[1] * (node.shape[1] if len(node.shape) > 1 else 1)
            elif node.op_type in [IROpType.ADD, IROpType.SUB, IROpType.MUL, IROpType.DIV, IROpType.RELU]:
                elems = 1
                if node.shape:
                    for dim in node.shape:
                        elems *= dim
                count += elems
            elif node.op_type == IROpType.DOT and node.shape:
                count += 2 * node.shape[0]
        return max(count, len(self.nodes))
