"""
hyper/workload/graph.py
=======================
Machine-readable Operation and Computation Graph models.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional


@dataclass
class OpNode:
    op_id: str
    op_type: str  # "matmul", "fft", "conv", "activation", "reduce", "gather", "render"
    input_shapes: List[List[int]] = field(default_factory=list)
    output_shape: List[int] = field(default_factory=list)
    flops_baseline: int = 0
    is_critical_path: bool = True
    is_redundant: bool = False
    is_dead: bool = False
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ComputationGraph:
    graph_id: str
    nodes: Dict[str, OpNode] = field(default_factory=dict)
    total_baseline_flops: int = 0
    total_hyper_flops: int = 0

    def add_node(self, node: OpNode) -> None:
        self.nodes[node.op_id] = node
        self.total_baseline_flops += node.flops_baseline
