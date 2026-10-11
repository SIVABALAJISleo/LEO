"""
hyper_universal/workload_ir/graph.py
Computational Intermediate Representation (IR) defining Dependency, Memory,
and Resource Graphs for mathematical bottleneck analysis and transformation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class OpKind(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    MATMUL = "MATMUL"
    CONV2D = "CONV2D"
    ELEMENTWISE = "ELEMENTWISE"
    REDUCTION = "REDUCTION"
    TRANSPOSE = "TRANSPOSE"
    FFT = "FFT"
    SORT = "SORT"
    STREAM_READ = "STREAM_READ"
    STREAM_WRITE = "STREAM_WRITE"
    CUSTOM = "CUSTOM"


@dataclass
class IRNode:
    node_id: str
    kind: OpKind
    shape: Tuple[int, ...]
    dtype: str = "float32"
    inputs: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    estimated_flops: int = 0
    memory_bytes: int = 0
    is_live: bool = True

    def __post_init__(self):
        if self.memory_bytes == 0 and len(self.shape) > 0:
            bytes_per_elem = 4 if self.dtype in ("float32", "int32") else (2 if self.dtype in ("float16", "int16") else 1)
            self.memory_bytes = int(np.prod(self.shape)) * bytes_per_elem


class ComputationalIR:
    """
    DAG representation of a computational workload providing dependency,
    memory, and resource graphs for bottleneck analysis.
    """

    def __init__(self, name: str = "workload_ir"):
        self.name = name
        self.nodes: Dict[str, IRNode] = {}
        self.inputs: List[str] = []
        self.outputs: List[str] = []

    def add_input(self, name: str, shape: Tuple[int, ...], dtype: str = "float32") -> str:
        node = IRNode(node_id=name, kind=OpKind.INPUT, shape=shape, dtype=dtype)
        self.nodes[name] = node
        self.inputs.append(name)
        return name

    def add_op(
        self,
        node_id: str,
        kind: OpKind,
        inputs: List[str],
        shape: Tuple[int, ...],
        dtype: str = "float32",
        flops: int = 0,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> str:
        node = IRNode(
            node_id=node_id,
            kind=kind,
            shape=shape,
            dtype=dtype,
            inputs=inputs,
            estimated_flops=flops,
            attributes=attrs or {},
        )
        self.nodes[node_id] = node
        return node_id

    def mark_output(self, node_id: str):
        if node_id in self.nodes and node_id not in self.outputs:
            self.outputs.append(node_id)

    def compute_dependency_graph(self) -> Dict[str, List[str]]:
        """Returns adjacency list representation of forward dataflow dependencies."""
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for nid, node in self.nodes.items():
            for inp in node.inputs:
                if inp in adj:
                    adj[inp].append(nid)
        return adj

    def get_peak_intermediate_memory(self) -> int:
        """Calculates peak concurrent intermediate tensor memory (bytes)."""
        return sum(node.memory_bytes for node in self.nodes.values() if node.kind != OpKind.INPUT)

    def get_total_flops(self) -> int:
        """Sums estimated theoretical FLOPs across all operations."""
        return sum(node.estimated_flops for node in self.nodes.values())

    def prune_dead_nodes(self) -> int:
        """Eliminates unreachable nodes not contributing to any marked output."""
        live: Set[str] = set()
        stack = list(self.outputs)
        while stack:
            cur = stack.pop()
            if cur in live:
                continue
            live.add(cur)
            if cur in self.nodes:
                for inp in self.nodes[cur].inputs:
                    stack.append(inp)

        pruned = 0
        for nid, node in list(self.nodes.items()):
            if nid not in live and node.kind != OpKind.INPUT:
                node.is_live = False
                pruned += 1
        return pruned

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "total_nodes": len(self.nodes),
            "total_flops": self.get_total_flops(),
            "peak_memory_bytes": self.get_peak_intermediate_memory(),
            "nodes": {
                nid: {
                    "kind": n.kind.value,
                    "shape": list(n.shape),
                    "dtype": n.dtype,
                    "inputs": n.inputs,
                    "flops": n.estimated_flops,
                    "bytes": n.memory_bytes,
                    "is_live": n.is_live,
                }
                for nid, n in self.nodes.items()
            },
        }
