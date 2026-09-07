"""
hyper_x/info_boundary/compiler.py
=============================================================================
HYPER-X Information Boundary Compiler & Information Dependency Graph
=============================================================================
Determines the minimum information required to satisfy the declared contract.

For every output observable:
  output -> dependency analysis -> necessary inputs -> intermediate states -> dispensable information

Classifies nodes into 7 strict categories:
  - ESSENTIAL:       Indispensable computation required for the observable
  - REDUNDANT:       Provably unreferenced or canceled computation (dead/noop)
  - PREDICTABLE:     High temporal/spatial correlation, amenable to cheap extrapolation
  - CACHED:          Already computed in prior epoch/frame or identical subproblem
  - APPROXIMABLE:    Tolerates low precision, quantization, or surrogate representation
  - RECONSTRUCTABLE: Can be recovered from sparse samples via bilateral/filter/upscale
  - UNKNOWN:         Indeterminate influence.

ABSOLUTE LAW: UNKNOWN must NEVER automatically become REDUNDANT.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
import numpy as np

class NodeType(str, enum.Enum):
    INPUT = "input"
    INTERMEDIATE = "intermediate"
    TRANSFORMATION = "transformation"
    STATE = "state"
    OUTPUT = "output"
    OBSERVABLE = "observable"
    CONSTRAINT = "constraint"

class EdgeType(str, enum.Enum):
    DEPENDS_ON = "depends_on"
    INFLUENCES = "influences"
    REQUIRED_FOR = "required_for"
    RECONSTRUCTS = "reconstructs"
    APPROXIMATES = "approximates"
    CACHES = "caches"
    PREDICTS = "predicts"

class NecessityClassification(str, enum.Enum):
    ESSENTIAL = "ESSENTIAL"
    REDUNDANT = "REDUNDANT"
    PREDICTABLE = "PREDICTABLE"
    CACHED = "CACHED"
    APPROXIMABLE = "APPROXIMABLE"
    RECONSTRUCTABLE = "RECONSTRUCTABLE"
    UNKNOWN = "UNKNOWN"

@dataclass
class InfoNode:
    node_id: str
    node_type: NodeType
    classification: NecessityClassification = NecessityClassification.UNKNOWN
    estimated_flops: float = 0.0
    memory_bytes: int = 0
    entropy: float = 1.0  # Normalized entropy [0.0, 1.0]
    sparsity: float = 0.0  # Sparsity ratio [0.0, 1.0]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InfoEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0

class InformationDependencyGraph:
    """Directed dependency and causal information graph for a workload."""

    def __init__(self, workload_id: str):
        self.workload_id = workload_id
        self.nodes: Dict[str, InfoNode] = {}
        self.edges: List[InfoEdge] = []
        self.adj_outgoing: Dict[str, List[InfoEdge]] = {}
        self.adj_incoming: Dict[str, List[InfoEdge]] = {}

    def add_node(self, node: InfoNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.adj_outgoing:
            self.adj_outgoing[node.node_id] = []
        if node.node_id not in self.adj_incoming:
            self.adj_incoming[node.node_id] = []

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, weight: float = 1.0) -> None:
        edge = InfoEdge(source_id=source_id, target_id=target_id, edge_type=edge_type, weight=weight)
        self.edges.append(edge)
        self.adj_outgoing.setdefault(source_id, []).append(edge)
        self.adj_incoming.setdefault(target_id, []).append(edge)

    def get_essential_subgraph(self) -> Set[str]:
        """Traverse backwards from observables/outputs to identify the indispensable closure."""
        visited = set()
        stack = [nid for nid, node in self.nodes.items() if node.node_type in [NodeType.OUTPUT, NodeType.OBSERVABLE]]

        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            for edge in self.adj_incoming.get(curr, []):
                if edge.edge_type in [EdgeType.DEPENDS_ON, EdgeType.REQUIRED_FOR, EdgeType.RECONSTRUCTS]:
                    stack.append(edge.source_id)

        return visited

class InformationBoundaryCompiler:
    """Analyzes a workload's information dependencies and synthesizes the minimum required compute."""

    def analyze_matrix_workload(self, A: np.ndarray, B: np.ndarray, tolerance: float = 1e-4) -> InformationDependencyGraph:
        graph = InformationDependencyGraph(workload_id="GEMM_InfoBoundary")

        # Analyze input A
        a_sparse = float(np.mean(np.abs(A) < 1e-6))
        u, s, vt = np.linalg.svd(A, full_matrices=False)
        eff_rank = int(np.sum(s > (s[0] * 1e-3)))
        rank_ratio = eff_rank / max(1, min(A.shape))

        node_a = InfoNode(
            node_id="input_A",
            node_type=NodeType.INPUT,
            classification=NecessityClassification.ESSENTIAL,
            memory_bytes=A.nbytes,
            sparsity=a_sparse,
            metadata={"shape": list(A.shape), "effective_rank": eff_rank, "rank_ratio": rank_ratio}
        )
        graph.add_node(node_a)

        # Analyze input B
        b_sparse = float(np.mean(np.abs(B) < 1e-6))
        node_b = InfoNode(
            node_id="input_B",
            node_type=NodeType.INPUT,
            classification=NecessityClassification.ESSENTIAL,
            memory_bytes=B.nbytes,
            sparsity=b_sparse,
            metadata={"shape": list(B.shape)}
        )
        graph.add_node(node_b)

        # Intermediate full dot product
        m, k = A.shape
        _, n = B.shape
        total_flops = 2.0 * m * k * n
        is_approximable = (rank_ratio < 0.5) or (a_sparse > 0.4) or (tolerance >= 1e-3)
        classification = NecessityClassification.APPROXIMABLE if is_approximable else NecessityClassification.ESSENTIAL

        node_mult = InfoNode(
            node_id="dense_matmul_op",
            node_type=NodeType.TRANSFORMATION,
            classification=classification,
            estimated_flops=total_flops,
            metadata={"algorithm": "BLAS_GEMM", "can_sparsify": a_sparse > 0.3, "can_factorize": rank_ratio < 0.5}
        )
        graph.add_node(node_mult)
        graph.add_edge("input_A", "dense_matmul_op", EdgeType.DEPENDS_ON)
        graph.add_edge("input_B", "dense_matmul_op", EdgeType.DEPENDS_ON)

        # Output observable
        node_out = InfoNode(
            node_id="output_C",
            node_type=NodeType.OUTPUT,
            classification=NecessityClassification.ESSENTIAL,
            memory_bytes=m * n * 4,
            metadata={"shape": [m, n], "tolerance": tolerance}
        )
        graph.add_node(node_out)
        graph.add_edge("dense_matmul_op", "output_C", EdgeType.REQUIRED_FOR)

        return graph

    def compile_summary(self, graph: InformationDependencyGraph) -> Dict[str, Any]:
        total_flops = sum(n.estimated_flops for n in graph.nodes.values())
        essential_nodes = graph.get_essential_subgraph()
        
        classifications = {c.value: 0 for c in NecessityClassification}
        for n in graph.nodes.values():
            classifications[n.classification.value] += 1

        dispensable_count = classifications[NecessityClassification.REDUNDANT.value] + \
                            classifications[NecessityClassification.CACHED.value] + \
                            classifications[NecessityClassification.PREDICTABLE.value]

        return {
            "workload_id": graph.workload_id,
            "total_nodes": len(graph.nodes),
            "essential_closure_size": len(essential_nodes),
            "classifications": classifications,
            "total_flops_baseline": total_flops,
            "dispensable_node_count": dispensable_count,
            "reduction_potential": dispensable_count / max(1, len(graph.nodes))
        }
