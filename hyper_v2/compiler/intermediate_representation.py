"""
hyper_v2/compiler/intermediate_representation.py
Directed Acyclic Graph (DAG) intermediate representation for computational workloads.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class DeviceTarget(str, Enum):
    CPU_PCORE = "CPU_PCORE"
    CPU_ECORE = "CPU_ECORE"
    INTEL_IGPU = "INTEL_IGPU"
    FIXED_ASIC_QUICKSYNC = "FIXED_ASIC_QUICKSYNC"
    HYBRID_CPU_IGPU = "HYBRID_CPU_IGPU"


class OpCategory(str, Enum):
    MATMUL = "MATMUL"
    CONV = "CONV"
    FFT = "FFT"
    REDUCTION = "REDUCTION"
    ELEMENTWISE = "ELEMENTWISE"
    ATTENTION = "ATTENTION"
    RAY_INTERSECT = "RAY_INTERSECT"
    N_BODY_INTERACT = "N_BODY_INTERACT"
    SORT_BVH = "SORT_BVH"
    SAMPLE_MC = "SAMPLE_MC"
    MEDIA_ENCODE = "MEDIA_ENCODE"
    EMBEDDING_LOOKUP = "EMBEDDING_LOOKUP"


@dataclass
class TensorSpec:
    name: str
    shape: Tuple[int, ...]
    dtype: str = "float32"
    sparsity_ratio: float = 0.0
    is_constant: bool = False
    estimated_bytes: int = 0

    def __post_init__(self):
        if self.estimated_bytes == 0 and len(self.shape) > 0:
            elem_size = 4 if "32" in self.dtype else (2 if "16" in self.dtype else (8 if "64" in self.dtype else 1))
            total_elems = 1
            for dim in self.shape:
                total_elems *= max(1, dim)
            self.estimated_bytes = int(total_elems * elem_size)


@dataclass
class IRNode:
    id: str
    op_type: OpCategory
    inputs: List[str]
    outputs: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)
    flop_cost: int = 0
    bytes_read: int = 0
    bytes_written: int = 0
    device_placement: DeviceTarget = DeviceTarget.CPU_PCORE
    is_fused: bool = False
    fused_nodes: List[str] = field(default_factory=list)
    can_eliminate: bool = False
    elimination_reason: Optional[str] = None
    substitute_algorithm: Optional[str] = None


@dataclass
class ComputationGraphIR:
    graph_id: str
    nodes: Dict[str, IRNode] = field(default_factory=dict)
    tensors: Dict[str, TensorSpec] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)
    total_flops: int = 0
    total_memory_traffic_bytes: int = 0

    def add_tensor(self, tensor: TensorSpec):
        self.tensors[tensor.name] = tensor

    def add_node(self, node: IRNode):
        self.nodes[node.id] = node
        if node.id not in self.execution_order:
            self.execution_order.append(node.id)
        self.recompute_totals()

    def recompute_totals(self):
        flops = 0
        traffic = 0
        for node in self.nodes.values():
            if not node.can_eliminate:
                flops += node.flop_cost
                traffic += (node.bytes_read + node.bytes_written)
        self.total_flops = flops
        self.total_memory_traffic_bytes = traffic

    def clone(self) -> "ComputationGraphIR":
        new_ir = ComputationGraphIR(graph_id=f"{self.graph_id}_opt")
        for k, v in self.tensors.items():
            new_ir.tensors[k] = TensorSpec(
                name=v.name, shape=v.shape, dtype=v.dtype,
                sparsity_ratio=v.sparsity_ratio, is_constant=v.is_constant,
                estimated_bytes=v.estimated_bytes
            )
        for k, v in self.nodes.items():
            new_ir.nodes[k] = IRNode(
                id=v.id, op_type=v.op_type, inputs=list(v.inputs), outputs=list(v.outputs),
                attributes=dict(v.attributes), flop_cost=v.flop_cost,
                bytes_read=v.bytes_read, bytes_written=v.bytes_written,
                device_placement=v.device_placement, is_fused=v.is_fused,
                fused_nodes=list(v.fused_nodes), can_eliminate=v.can_eliminate,
                elimination_reason=v.elimination_reason,
                substitute_algorithm=v.substitute_algorithm
            )
        new_ir.execution_order = list(self.execution_order)
        new_ir.recompute_totals()
        return new_ir
