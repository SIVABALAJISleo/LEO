"""
hyper100/workload_analyzer.py
=============================
Workload Intelligence & Dependency Graph Extraction Engine.
Transforms computational tasks into formal Directed Acyclic Graphs (DAGs)
to detect operation dependencies, arithmetic intensity, memory movement,
and optimal hardware suitability (CPU AVX2 vs. Intel UHD Xe EUs).
"""

import time
import hashlib
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ComputationNode:
    """Represents a discrete computational operation in the dependency graph."""
    node_id: str
    op_type: str                   # 'matmul', 'conv2d', 'attention', 'fft', 'elementwise', 'reduction', etc.
    input_ids: List[str] = field(default_factory=list)
    output_shape: Tuple[int, ...] = ()
    dtype: str = "float32"
    estimated_flops: float = 0.0
    memory_bytes: int = 0
    arithmetic_intensity: float = 0.0  # FLOPs per byte transferred
    is_fusible: bool = False
    is_pure: bool = True
    cpu_suitability: float = 0.5   # 0.0 (unsuited) to 1.0 (highly suited)
    igpu_suitability: float = 0.5  # 0.0 (unsuited) to 1.0 (highly suited)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkloadProfile:
    """Machine-readable workload characterization report."""
    workload_name: str
    total_nodes: int
    total_estimated_flops: float
    total_memory_bytes: int
    arithmetic_intensity: float
    critical_path_length: int
    parallelism_degree: float
    recommended_primary_device: str  # 'CPU', 'INTEL_UHD', or 'HETEROGENEOUS_PIPELINE'
    fusion_opportunities: int
    redundancy_candidates: List[str]
    graph_signature: str


class ComputationGraph:
    """Directed Acyclic Graph representing the workload's computational operations."""
    def __init__(self, name: str = "computational_graph"):
        self.name = name
        self.nodes: Dict[str, ComputationNode] = {}
        self.edges: Dict[str, List[str]] = {}  # node_id -> list of successor node_ids
        self.in_degree: Dict[str, int] = {}

    def add_node(self, node: ComputationNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []
        if node.node_id not in self.in_degree:
            self.in_degree[node.node_id] = 0

        for inp in node.input_ids:
            if inp not in self.edges:
                self.edges[inp] = []
            self.edges[inp].append(node.node_id)
            self.in_degree[node.node_id] += 1

    def topological_sort(self) -> List[ComputationNode]:
        """Returns nodes in valid execution order using Kahn's algorithm."""
        in_deg = dict(self.in_degree)
        queue = [n_id for n_id, d in in_deg.items() if d == 0]
        sorted_nodes = []

        while queue:
            curr_id = queue.pop(0)
            if curr_id in self.nodes:
                sorted_nodes.append(self.nodes[curr_id])
            for neighbor in self.edges.get(curr_id, []):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        return sorted_nodes

    def compute_signature(self) -> str:
        """Computes a deterministic hash of the graph structure."""
        ordered = sorted(self.nodes.keys())
        sig_str = "|".join(f"{n}:{self.nodes[n].op_type}:{self.nodes[n].output_shape}" for n in ordered)
        return hashlib.sha256(sig_str.encode("utf-8")).hexdigest()[:16]


class WorkloadAnalyzer:
    """Analyzes raw tensors, callables, or graph descriptions to extract WorkloadProfile."""

    @staticmethod
    def analyze_matmul(A: np.ndarray, B: np.ndarray, name: str = "matmul_workload") -> Tuple[ComputationGraph, WorkloadProfile]:
        graph = ComputationGraph(name=name)
        M, K = A.shape
        K2, N = B.shape
        flops = 2.0 * M * N * K
        mem_bytes = (A.nbytes + B.nbytes + M * N * 4)
        intensity = flops / max(mem_bytes, 1)

        # Matmul arithmetic intensity is high for large N, M, K
        igpu_suit = min(1.0, max(0.2, (M * N * K) / (1024 ** 3 * 2.0) + (intensity / 50.0)))
        cpu_suit = min(1.0, max(0.4, 1.0 - igpu_suit * 0.5))

        node = ComputationNode(
            node_id="matmul_0",
            op_type="matmul",
            input_ids=["input_A", "input_B"],
            output_shape=(M, N),
            dtype=str(A.dtype),
            estimated_flops=flops,
            memory_bytes=mem_bytes,
            arithmetic_intensity=intensity,
            is_fusible=True,
            is_pure=True,
            cpu_suitability=cpu_suit,
            igpu_suitability=igpu_suit,
            metadata={"M": M, "N": N, "K": K}
        )
        graph.add_node(node)

        primary_device = "INTEL_UHD" if (igpu_suit > 0.75 and M >= 512) else ("CPU" if M < 128 else "HETEROGENEOUS_PIPELINE")

        profile = WorkloadProfile(
            workload_name=name,
            total_nodes=1,
            total_estimated_flops=flops,
            total_memory_bytes=mem_bytes,
            arithmetic_intensity=intensity,
            critical_path_length=1,
            parallelism_degree=float(M * N),
            recommended_primary_device=primary_device,
            fusion_opportunities=0,
            redundancy_candidates=["input_A_static" if M == K else "none"],
            graph_signature=graph.compute_signature()
        )
        return graph, profile

    @staticmethod
    def analyze_conv2d(image_shape: Tuple[int, int, int, int], kernel_shape: Tuple[int, int, int, int], name: str = "conv2d_workload") -> Tuple[ComputationGraph, WorkloadProfile]:
        N, C, H, W = image_shape
        K, _, Kh, Kw = kernel_shape
        out_H, out_W = H - Kh + 1, W - Kw + 1
        flops = 2.0 * N * K * out_H * out_W * C * Kh * Kw
        mem_bytes = (N * C * H * W + K * C * Kh * Kw + N * K * out_H * out_W) * 4
        intensity = flops / max(mem_bytes, 1)

        graph = ComputationGraph(name=name)
        node = ComputationNode(
            node_id="conv2d_0",
            op_type="conv2d",
            input_ids=["input_tensor", "filter_weights"],
            output_shape=(N, K, out_H, out_W),
            dtype="float32",
            estimated_flops=flops,
            memory_bytes=mem_bytes,
            arithmetic_intensity=intensity,
            is_fusible=True,
            is_pure=True,
            cpu_suitability=0.6,
            igpu_suitability=0.85,
            metadata={"kernel_size": (Kh, Kw), "channels": C, "filters": K}
        )
        graph.add_node(node)

        profile = WorkloadProfile(
            workload_name=name,
            total_nodes=1,
            total_estimated_flops=flops,
            total_memory_bytes=mem_bytes,
            arithmetic_intensity=intensity,
            critical_path_length=1,
            parallelism_degree=float(N * K * out_H * out_W),
            recommended_primary_device="INTEL_UHD" if intensity > 15.0 else "CPU",
            fusion_opportunities=1,  # Bias + ReLU fusion
            redundancy_candidates=["spatial_coherence"],
            graph_signature=graph.compute_signature()
        )
        return graph, profile
