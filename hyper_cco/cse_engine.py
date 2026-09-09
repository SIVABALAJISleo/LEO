"""
hyper_cco/cse_engine.py
=======================
Graph-Level Redundancy Analysis & Common-Subexpression Elimination (CSE).
Detects duplicate computational nodes in workload DAGs (e.g., repeated A @ B, shared activations,
identical matrix tiles, intermediate embeddings) using structural hash-consing.
Executes shared subexpressions once and reuses them across the DAG.
"""

from typing import Dict, Any, List, Tuple, Optional, Set, Callable
import hashlib
import time
import numpy as np


class DagNode:
    """A node in the computation DAG representing an operation or input."""
    def __init__(
        self,
        node_id: str,
        op_name: str,
        inputs: List['DagNode'],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.op_name = op_name
        self.inputs = inputs
        self.metadata = metadata or {}
        self.cached_hash: Optional[str] = None
        self.evaluated_value: Optional[Any] = None
        self.ref_count: int = 0

    def compute_structural_hash(self) -> str:
        """
        Hash-consing: recursively computes a unique deterministic hash based on
        op_name, structural input dependencies, and constant metadata.
        """
        if self.cached_hash is not None:
            return self.cached_hash

        hasher = hashlib.sha256()
        hasher.update(self.op_name.encode("utf-8"))
        for inp in self.inputs:
            hasher.update(inp.compute_structural_hash().encode("utf-8"))

        # Include constant metadata if present
        for k in sorted(self.metadata.keys()):
            v = self.metadata[k]
            if isinstance(v, np.ndarray):
                hasher.update(f"{k}=".encode("utf-8") + v.tobytes())
            else:
                hasher.update(f"{k}={v}".encode("utf-8"))

        self.cached_hash = hasher.hexdigest()[:24]
        return self.cached_hash


class CommonSubexpressionEngine:
    """
    DAG optimizer that discovers and eliminates identical sub-computations.
    """
    def __init__(self):
        self.canonical_table: Dict[str, DagNode] = {}
        self.eliminated_subexpressions: int = 0
        self.saved_operations: float = 0.0

    def register_or_reuse(self, node: DagNode, op_cost: float = 0.0) -> Tuple[DagNode, bool]:
        """
        Registers a node. If an identical structural subexpression already exists in the DAG,
        returns the canonical node and marks reused=True.
        """
        struct_hash = node.compute_structural_hash()
        if struct_hash in self.canonical_table:
            canonical = self.canonical_table[struct_hash]
            canonical.ref_count += 1
            self.eliminated_subexpressions += 1
            self.saved_operations += op_cost
            return canonical, True

        self.canonical_table[struct_hash] = node
        node.ref_count = 1
        return node, False

    def optimize_dag(self, root_nodes: List[DagNode]) -> Dict[str, Any]:
        """
        Traverses a DAG, deduplicating equivalent nodes and counting work elimination.
        """
        visited: Set[str] = set()
        unique_nodes = 0
        reused_nodes = 0

        def traverse(node: DagNode):
            nonlocal unique_nodes, reused_nodes
            node_hash = node.compute_structural_hash()
            if node_hash in visited:
                reused_nodes += 1
                return
            visited.add(node_hash)
            unique_nodes += 1
            for child in node.inputs:
                traverse(child)

        for root in root_nodes:
            traverse(root)

        return {
            "total_visited": len(visited),
            "unique_nodes": unique_nodes,
            "reused_nodes": reused_nodes,
            "eliminated_subexpressions": self.eliminated_subexpressions,
            "saved_operations": self.saved_operations,
        }
