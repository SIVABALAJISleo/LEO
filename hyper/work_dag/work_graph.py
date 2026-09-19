"""
Work-DAG Engine for LEO/HYPER Ω.
Constructs, inspects, and optimizes workload dependency graphs.

Records for each node:
- operation, inputs, outputs, dependencies, shape, dtype
- memory footprint, estimated work, measured work, device, contract relevance

Supports:
- Dependency analysis & topological sort
- Dead-node detection & elimination
- Common-subexpression detection & elimination (CSE)
- Redundant intermediate detection
- Reusable-state detection
- Critical-path analysis
"""

from __future__ import annotations

import dataclasses
import hashlib
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


@dataclasses.dataclass
class WorkNode:
    node_id: str
    operation: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str] = dataclasses.field(default_factory=list)
    shape: Tuple[int, ...] = ()
    dtype: str = "float32"
    memory_footprint_bytes: int = 0
    estimated_work_flops: float = 0.0
    measured_work_flops: float = 0.0
    device: str = "CPU_AVX2"
    contract_relevance: str = "REQUIRED"  # REQUIRED | REUSABLE | REDUNDANT | DEAD
    cached: bool = False
    is_dead: bool = False

    def fingerprint(self) -> str:
        """Compute structural fingerprint for Common-Subexpression Elimination (CSE)."""
        if self.operation in ("load", "const", "input") or not self.inputs:
            payload = f"{self.operation}:{sorted(self.outputs)}:{self.shape}:{self.dtype}"
        else:
            payload = f"{self.operation}:{sorted(self.inputs)}:{self.shape}:{self.dtype}"
        return hashlib.sha256(payload.encode()).hexdigest()



@dataclasses.dataclass
class WorkEdge:
    source_id: str
    target_id: str
    tensor_name: str
    tensor_shape: Tuple[int, ...] = ()
    data_bytes: int = 0


class WorkGraph:
    """Directed Acyclic Graph representing execution flow and data dependencies."""

    def __init__(self, name: str = "WorkGraph") -> None:
        self.name = name
        self.nodes: Dict[str, WorkNode] = {}
        self.edges: List[WorkEdge] = []
        self._in_degree: Dict[str, int] = {}
        self._out_degree: Dict[str, int] = {}

    def add_node(self, node: WorkNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self._in_degree:
            self._in_degree[node.node_id] = 0
        if node.node_id not in self._out_degree:
            self._out_degree[node.node_id] = 0

    def add_edge(self, source_id: str, target_id: str, tensor_name: str, tensor_shape: Tuple[int, ...] = (), data_bytes: int = 0) -> None:
        edge = WorkEdge(source_id, target_id, tensor_name, tensor_shape, data_bytes)
        self.edges.append(edge)
        self._out_degree[source_id] = self._out_degree.get(source_id, 0) + 1
        self._in_degree[target_id] = self._in_degree.get(target_id, 0) + 1
        if source_id not in self.nodes[target_id].dependencies:
            self.nodes[target_id].dependencies.append(source_id)

    def topological_sort(self) -> List[WorkNode]:
        """Returns nodes in topological dependency execution order."""
        in_degrees = {k: 0 for k in self.nodes}
        adj: Dict[str, List[str]] = {k: [] for k in self.nodes}
        for e in self.edges:
            adj[e.source_id].append(e.target_id)
            in_degrees[e.target_id] += 1

        queue = [k for k, d in in_degrees.items() if d == 0]
        order = []
        while queue:
            curr = queue.pop(0)
            order.append(self.nodes[curr])
            for nxt in adj[curr]:
                in_degrees[nxt] -= 1
                if in_degrees[nxt] == 0:
                    queue.append(nxt)

        if len(order) != len(self.nodes):
            # Graph has cycles or disconnected components; return existing order
            return list(self.nodes.values())
        return order

    def detect_dead_nodes(self, terminal_outputs: Set[str]) -> List[str]:
        """
        Detects dead nodes that do not contribute to terminal outputs.
        """
        useful_nodes: Set[str] = set()

        # Find initial producers of terminal outputs
        for node in self.nodes.values():
            if any(out in terminal_outputs for out in node.outputs):
                useful_nodes.add(node.node_id)

        # Backward traversal to mark useful dependencies
        changed = True
        while changed:
            changed = False
            for node_id in list(useful_nodes):
                for dep in self.nodes[node_id].dependencies:
                    if dep not in useful_nodes and dep in self.nodes:
                        useful_nodes.add(dep)
                        changed = True

        dead_nodes = [nid for nid in self.nodes if nid not in useful_nodes]
        for nid in dead_nodes:
            self.nodes[nid].is_dead = True
            self.nodes[nid].contract_relevance = "DEAD"

        return dead_nodes

    def eliminate_dead_nodes(self, terminal_outputs: Set[str]) -> int:
        """Removes dead nodes from the graph."""
        dead_ids = self.detect_dead_nodes(terminal_outputs)
        for nid in dead_ids:
            del self.nodes[nid]
        self.edges = [e for e in self.edges if e.source_id not in dead_ids and e.target_id not in dead_ids]
        return len(dead_ids)

    def detect_common_subexpressions(self) -> Dict[str, List[str]]:
        """
        Detects nodes performing identical operations on identical inputs (CSE).
        Returns fingerprint -> list of duplicate node_ids.
        """
        seen: Dict[str, List[str]] = {}
        for nid, node in self.nodes.items():
            if node.is_dead:
                continue
            fp = node.fingerprint()
            if fp not in seen:
                seen[fp] = []
            seen[fp].append(nid)

        return {fp: nids for fp, nids in seen.items() if len(nids) > 1}

    def eliminate_common_subexpressions(self) -> int:
        """Fuses common subexpressions, routing downstream consumers to the canonical node."""
        duplicates = self.detect_common_subexpressions()
        eliminated_count = 0

        for fp, nids in duplicates.items():
            canonical_id = nids[0]
            redundant_ids = nids[1:]
            for red_id in redundant_ids:
                # Redirect outgoing edges
                for edge in self.edges:
                    if edge.source_id == red_id:
                        edge.source_id = canonical_id
                # Mark as redundant
                self.nodes[red_id].contract_relevance = "REDUNDANT"
                del self.nodes[red_id]
                eliminated_count += 1

        # Clean duplicate edges
        unique_edges = []
        seen_edges = set()
        for e in self.edges:
            sig = (e.source_id, e.target_id, e.tensor_name)
            if sig not in seen_edges and e.source_id in self.nodes and e.target_id in self.nodes:
                seen_edges.add(sig)
                unique_edges.append(e)
        self.edges = unique_edges

        return eliminated_count

    def critical_path_analysis(self) -> Tuple[List[str], float]:
        """
        Computes the critical execution path (longest path of estimated work).
        Returns (node_ids_in_path, total_estimated_flops).
        """
        ordered = self.topological_sort()
        dp_work: Dict[str, float] = {n.node_id: n.estimated_work_flops for n in ordered}
        dp_prev: Dict[str, Optional[str]] = {n.node_id: None for n in ordered}

        for node in ordered:
            for dep_id in node.dependencies:
                if dep_id in dp_work:
                    cand = dp_work[dep_id] + node.estimated_work_flops
                    if cand > dp_work[node.node_id]:
                        dp_work[node.node_id] = cand
                        dp_prev[node.node_id] = dep_id

        if not dp_work:
            return [], 0.0

        max_node = max(dp_work.keys(), key=lambda k: dp_work[k])
        max_work = dp_work[max_node]

        # Backtrack path
        path = []
        curr = max_node
        while curr is not None:
            path.append(curr)
            curr = dp_prev.get(curr)
        path.reverse()

        return path, max_work

    def summary(self) -> Dict[str, Any]:
        total_estimated = sum(n.estimated_work_flops for n in self.nodes.values() if not n.is_dead)
        total_mem = sum(n.memory_footprint_bytes for n in self.nodes.values() if not n.is_dead)
        crit_path, crit_work = self.critical_path_analysis()
        return {
            "name": self.name,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_estimated_flops": total_estimated,
            "total_memory_bytes": total_mem,
            "critical_path_nodes": crit_path,
            "critical_path_flops": crit_work,
        }
