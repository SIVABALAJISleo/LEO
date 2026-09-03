"""
hyper_v3/ir/node.py
Universal Computation IR Node representing operations, FLOPs, memory footprints, and constraints.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from hyper_v3.ir.operation import OpType, DeviceType
from hyper_v3.ir.tensor import TensorDescriptor
from hyper_v3.ir.annotations import NodeAnnotations


@dataclass
class IRNode:
    node_id: str
    op_type: OpType
    name: str
    inputs: List[TensorDescriptor] = field(default_factory=list)
    outputs: List[TensorDescriptor] = field(default_factory=list)
    flops: int = 0
    memory_reads_bytes: int = 0
    memory_writes_bytes: int = 0
    target_device: DeviceType = DeviceType.UNSPECIFIED
    latency_estimate_us: float = 0.0
    annotations: NodeAnnotations = field(default_factory=NodeAnnotations)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def calculate_memory_footprint(self) -> int:
        reads = sum(t.memory_bytes for t in self.inputs)
        writes = sum(t.memory_bytes for t in self.outputs)
        self.memory_reads_bytes = reads
        self.memory_writes_bytes = writes
        return reads + writes
