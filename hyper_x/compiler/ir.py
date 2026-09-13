#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compiler/ir.py
======================
Total GPU Omega: Universal HYPER-IR.

Represents:
  Tensors, Buffers, Images, Kernels, Graphs, Dependencies, Memory,
  Synchronization, Observables, Precision, and Contract Invariants.
"""

from __future__ import annotations
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np


class IROperation(str, Enum):
    MATMUL = "MATMUL"
    CONV2D = "CONV2D"
    ATTENTION = "ATTENTION"
    REDUCTION = "REDUCTION"
    ELEMENTWISE = "ELEMENTWISE"
    FFT = "FFT"
    ACTIVATION = "ACTIVATION"
    QUANTIZE = "QUANTIZE"
    DEQUANTIZE = "DEQUANTIZE"
    RESHAPE = "RESHAPE"
    MEMCOPY = "MEMCOPY"


@dataclass
class IRTensorDescriptor:
    tensor_id: str
    shape: Tuple[int, ...]
    dtype: str = "float32"
    is_sparse: bool = False
    sparsity_ratio: float = 0.0
    effective_rank: Optional[int] = None
    locality_hint: str = "L2_CACHE"


@dataclass
class IRNode:
    """Atomic operation node in the Universal HYPER-IR computational graph."""
    node_id: str
    op: IROperation
    inputs: List[str]                  # tensor_ids
    outputs: List[str]                 # tensor_ids
    attributes: Dict[str, Any] = field(default_factory=dict)
    contract_tolerance: float = 1e-4
    estimated_flops: float = 0.0
    memory_footprint_bytes: int = 0
    is_eliminated: bool = False
    is_fused: bool = False
    fused_into: Optional[str] = None

    def mark_eliminated(self):
        self.is_eliminated = True


class IRGraph:
    """Computational DAG representation in Universal HYPER-IR."""

    def __init__(self, graph_id: str = "hyper_ir_graph"):
        self.graph_id = graph_id
        self.nodes: Dict[str, IRNode] = {}
        self.tensors: Dict[str, IRTensorDescriptor] = {}
        self.inputs: List[str] = []
        self.outputs: List[str] = []

    def add_tensor(self, desc: IRTensorDescriptor) -> IRTensorDescriptor:
        self.tensors[desc.tensor_id] = desc
        return desc

    def add_node(self, node: IRNode) -> IRNode:
        self.nodes[node.node_id] = node
        return node

    def get_successors(self, node_id: str) -> List[IRNode]:
        node = self.nodes[node_id]
        out_tensors = set(node.outputs)
        successors = []
        for other in self.nodes.values():
            if not other.is_eliminated and any(inp in out_tensors for inp in other.inputs):
                successors.append(other)
        return successors

    def topological_sort(self) -> List[IRNode]:
        """Returns topological ordering of non-eliminated nodes."""
        in_degree = {nid: 0 for nid, n in self.nodes.items() if not n.is_eliminated}
        for n in self.nodes.values():
            if n.is_eliminated:
                continue
            for succ in self.get_successors(n.node_id):
                if succ.node_id in in_degree:
                    in_degree[succ.node_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        ordered = []
        while queue:
            curr = queue.pop(0)
            ordered.append(self.nodes[curr])
            for succ in self.get_successors(curr):
                if succ.node_id in in_degree:
                    in_degree[succ.node_id] -= 1
                    if in_degree[succ.node_id] == 0:
                        queue.append(succ.node_id)
        return ordered

    def summary(self) -> Dict[str, Any]:
        live_nodes = [n for n in self.nodes.values() if not n.is_eliminated]
        total_flops = sum(n.estimated_flops for n in live_nodes)
        return {
            "total_nodes": len(self.nodes),
            "live_nodes": len(live_nodes),
            "eliminated_nodes": len(self.nodes) - len(live_nodes),
            "total_estimated_flops": total_flops,
            "tensor_count": len(self.tensors)
        }
