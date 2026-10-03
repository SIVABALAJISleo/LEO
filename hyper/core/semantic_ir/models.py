"""
hyper/core/semantic_ir/models.py
Universal Canonical Computation Intermediate Representation (Semantic IR).
Preserves semantic invariants, tensor/scalar operations, loops, branches,
memory dependencies, side-effects, and device dispatch targets.
"""
from __future__ import annotations
import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class DeviceTarget(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_UHD_IGPU = "INTEL_UHD_IGPU"
    HYBRID_CPU_IGPU = "HYBRID_CPU_IGPU"


class SemanticOpCode(str, Enum):
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
    TOP_K = "TOP_K"
    SLICE = "SLICE"
    SPARSE_MATMUL = "SPARSE_MATMUL"
    DELTA_MATMUL = "DELTA_MATMUL"
    RANK1_UPDATE = "RANK1_UPDATE"
    LOOP_HEADER = "LOOP_HEADER"
    BRANCH = "BRANCH"
    OUTPUT = "OUTPUT"


class SemanticNode(BaseModel):
    node_id: str
    opcode: SemanticOpCode
    inputs: List[str] = Field(default_factory=list)
    shape: Optional[Tuple[int, ...]] = None
    dtype: str = "float64"
    device_target: DeviceTarget = DeviceTarget.CPU_AVX2
    attributes: Dict[str, Any] = Field(default_factory=dict)
    has_side_effects: bool = False
    is_dead: bool = False
    is_constant: bool = False
    constant_hash: Optional[str] = None


class CanonicalSemanticIR(BaseModel):
    """
    Authoritative Canonical Semantic IR DAG.
    """
    program_id: str
    nodes: Dict[str, SemanticNode] = Field(default_factory=dict)
    input_nodes: List[str] = Field(default_factory=list)
    output_nodes: List[str] = Field(default_factory=list)

    def add_node(self, node: SemanticNode) -> None:
        self.nodes[node.node_id] = node
        if node.opcode == SemanticOpCode.INPUT and node.node_id not in self.input_nodes:
            self.input_nodes.append(node.node_id)
        elif node.opcode == SemanticOpCode.OUTPUT and node.node_id not in self.output_nodes:
            self.output_nodes.append(node.node_id)

    def compute_semantic_hash(self) -> str:
        """Computes deterministic cryptographic hash of IR DAG topology and semantics."""
        elements = []
        for n_id in sorted(self.nodes.keys()):
            n = self.nodes[n_id]
            elements.append(f"{n.node_id}:{n.opcode.value}:{','.join(n.inputs)}:{n.shape}:{n.dtype}")
        raw = "|".join(elements)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_topological_sort(self) -> List[str]:
        """Returns topological ordering of nodes from inputs to outputs."""
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

    def count_symbolic_operations(self) -> int:
        """Calculates theoretical baseline FLOP count of the DAG."""
        count = 0
        for node in self.nodes.values():
            if node.is_dead:
                continue
            if node.opcode == SemanticOpCode.MATMUL and node.shape and len(node.shape) >= 2:
                # 2 * M * N * K
                k = node.shape[1] if len(node.shape) > 1 else node.shape[0]
                count += 2 * node.shape[0] * node.shape[1] * k
            elif node.opcode in [
                SemanticOpCode.ADD, SemanticOpCode.SUB, SemanticOpCode.MUL,
                SemanticOpCode.DIV, SemanticOpCode.RELU
            ]:
                elems = 1
                if node.shape:
                    for dim in node.shape:
                        elems *= dim
                count += elems
            elif node.opcode == SemanticOpCode.DOT and node.shape:
                count += 2 * node.shape[0]
            elif node.opcode == SemanticOpCode.CONV2D and node.shape:
                count += 4 * node.shape[0] * (node.shape[1] if len(node.shape) > 1 else 1)
        return max(count, len(self.nodes))
