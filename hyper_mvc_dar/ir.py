"""
hyper_mvc_dar/ir.py
Universal Computation Directed Acyclic Graph (DAG) Intermediate Representation (IR).
Tracks tensor shapes, dtypes, estimated vs measured FLOPs, memory footprints,
dependencies, and device affinities.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np


class DataType(Enum):
    FP64 = "float64"
    FP32 = "float32"
    FP16 = "float16"
    BF16 = "bfloat16"
    INT32 = "int32"
    INT8 = "int8"
    INT4 = "int4"
    TERNARY = "ternary_b1.58"
    BOOL = "bool"


class OpType(Enum):
    MATMUL = "matmul"
    CONV2D = "conv2d"
    FFT = "fft"
    REDUCTION = "reduction"
    ELEMENTWISE = "elementwise"
    ACTIVATION = "activation"
    SORT = "sort"
    SEARCH = "search"
    RAY_TRACE = "ray_trace"
    N_BODY = "n_body"
    CUSTOM = "custom"


@dataclass
class TensorDescriptor:
    name: str
    shape: Tuple[int, ...]
    dtype: DataType
    sparsity: float = 0.0
    effective_rank: Optional[int] = None
    memory_bytes: int = 0

    def __post_init__(self):
        if self.memory_bytes == 0 and len(self.shape) > 0:
            elem_count = 1
            for d in self.shape:
                elem_count *= d
            bytes_per_elem = 4
            if self.dtype in (DataType.FP64,):
                bytes_per_elem = 8
            elif self.dtype in (DataType.FP16, DataType.BF16):
                bytes_per_elem = 2
            elif self.dtype in (DataType.INT8,):
                bytes_per_elem = 1
            elif self.dtype in (DataType.TERNARY, DataType.INT4):
                bytes_per_elem = 1  # Packed representation
            self.memory_bytes = int(elem_count * bytes_per_elem * (1.0 - self.sparsity))


@dataclass
class OpNode:
    node_id: str
    op_type: OpType
    inputs: List[str]
    outputs: List[str]
    estimated_flops: int = 0
    measured_flops: Optional[int] = None
    memory_reads: int = 0
    memory_writes: int = 0
    device_affinity: str = "AUTO"  # "CPU_P_CORE", "CPU_E_CORE", "INTEL_IGPU", "AUTO"
    fused_into: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def arithmetic_intensity(self) -> float:
        total_bytes = self.memory_reads + self.memory_writes
        if total_bytes == 0:
            return float(self.estimated_flops)
        return self.estimated_flops / total_bytes


class ComputationGraph:
    """Universal DAG representing full workload execution."""

    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, OpNode] = {}
        self.tensors: Dict[str, TensorDescriptor] = {}
        self.entry_inputs: List[str] = []
        self.terminal_outputs: List[str] = []

    def add_tensor(self, tensor: TensorDescriptor):
        self.tensors[tensor.name] = tensor

    def add_node(self, node: OpNode):
        self.nodes[node.node_id] = node

    def get_predecessors(self, node_id: str) -> List[OpNode]:
        node = self.nodes.get(node_id)
        if not node:
            return []
        preds = []
        for other_id, other in self.nodes.items():
            if any(out in node.inputs for out in other.outputs):
                preds.append(other)
        return preds

    def get_successors(self, node_id: str) -> List[OpNode]:
        node = self.nodes.get(node_id)
        if not node:
            return []
        succs = []
        for other_id, other in self.nodes.items():
            if any(inp in node.outputs for inp in other.inputs):
                succs.append(other)
        return succs

    def total_estimated_flops(self) -> int:
        return sum(n.estimated_flops for n in self.nodes.values() if not n.fused_into)

    def total_memory_footprint(self) -> int:
        return sum(t.memory_bytes for t in self.tensors.values())

    def topological_sort(self) -> List[OpNode]:
        visited: Set[str] = set()
        stack: List[OpNode] = []

        def dfs(nid: str):
            visited.add(nid)
            node = self.nodes[nid]
            for succ in self.get_successors(nid):
                if succ.node_id not in visited:
                    dfs(succ.node_id)
            stack.insert(0, node)

        for nid in self.nodes:
            if nid not in visited:
                dfs(nid)
        return stack
