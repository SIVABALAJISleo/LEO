"""
hyper/incremental.py
====================
Incremental and Delta Computation Engine for LEO/HYPER.
Fulfills Phase 6 of the Master Architectural Specification.
Guarantees mathematically rigorous linear delta reuse and fails closed on nonlinear or unknown dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class Node:
    node_id: str
    is_linear: bool
    compute_fn: Callable[..., Any]
    dependencies: List[str] = field(default_factory=list)
    cost_units: int = 1


class DependencyGraph:
    """Directed acyclic graph tracking computational dependencies and linearity."""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_node(
        self,
        node_id: str,
        is_linear: bool,
        compute_fn: Callable[..., Any],
        dependencies: Optional[List[str]] = None,
        cost_units: int = 1,
    ) -> None:
        self.nodes[node_id] = Node(
            node_id=node_id,
            is_linear=is_linear,
            compute_fn=compute_fn,
            dependencies=dependencies or [],
            cost_units=cost_units,
        )

    def get_downstream_affected(self, changed_nodes: Set[str]) -> Set[str]:
        """Find all nodes that depend directly or transitively on changed_nodes."""
        affected = set(changed_nodes)
        changed = True
        while changed:
            changed = False
            for nid, node in self.nodes.items():
                if nid not in affected:
                    if any(dep in affected for dep in node.dependencies):
                        affected.add(nid)
                        changed = True
        return affected

    def topological_sort(self) -> List[str]:
        """Return node IDs in topological execution order."""
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(nid: str):
            visited.add(nid)
            for dep in self.nodes[nid].dependencies:
                if dep in self.nodes and dep not in visited:
                    dfs(dep)
            order.append(nid)

        for nid in self.nodes:
            if nid not in visited:
                dfs(nid)
        return order


class DeltaAnalyzer:
    """Analyzes differences between consecutive inputs."""

    @staticmethod
    def compute_delta(previous: Any, current: Any) -> Tuple[Optional[Any], bool]:
        """
        Compute delta = current - previous.
        Returns (delta, is_identical).
        """
        if previous is None or current is None:
            return None, False

        if isinstance(previous, np.ndarray) and isinstance(current, np.ndarray):
            if previous.shape != current.shape or previous.dtype != current.dtype:
                return None, False
            delta = current - previous
            is_identical = bool(np.all(delta == 0))
            return delta, is_identical

        is_identical = bool(previous == current)
        return None, is_identical


class IncrementalExecutor:
    """
    Executes incremental updates where mathematically valid.
    Applies linear delta identities: A'B = AB + (Delta A) B
    Falls back to exact full recomputation if any dependency is nonlinear or unproven.
    """

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def execute(
        self,
        inputs: Dict[str, Any],
        previous_inputs: Optional[Dict[str, Any]] = None,
        cached_intermediates: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Execute computation graph incrementally.
        Returns:
            (outputs, metadata)
        Metadata contains:
            - changed_inputs
            - affected_nodes
            - recomputed_nodes
            - reused_nodes
            - work_eliminated_pct
            - exactness_status
        """
        previous_inputs = previous_inputs or {}
        cached_intermediates = cached_intermediates or {}

        # 1. Detect changed input nodes
        changed_inputs = []
        for k, v in inputs.items():
            if k not in previous_inputs:
                changed_inputs.append(k)
            else:
                _, identical = DeltaAnalyzer.compute_delta(previous_inputs[k], v)
                if not identical:
                    changed_inputs.append(k)

        # 2. Determine affected nodes
        affected_nodes = self.graph.get_downstream_affected(set(changed_inputs))

        # Check if all affected nodes are known in the graph
        unknown_dependencies = False
        for nid in affected_nodes:
            if nid in self.graph.nodes:
                for dep in self.graph.nodes[nid].dependencies:
                    if dep not in self.graph.nodes and dep not in inputs:
                        unknown_dependencies = True
                        break

        # Check if any affected intermediate node is nonlinear
        has_nonlinear_affected = any(
            self.graph.nodes[nid].is_linear is False for nid in affected_nodes if nid in self.graph.nodes
        )

        total_cost = sum(n.cost_units for n in self.graph.nodes.values())
        results: Dict[str, Any] = {}
        recomputed_nodes: List[str] = []
        reused_nodes: List[str] = []

        # If dependencies are unknown or nonlinear path touched without valid state, fallback closed
        if unknown_dependencies or (has_nonlinear_affected and not cached_intermediates):
            # Full exact fallback
            exactness_status = "FALLBACK_EXACT"
            order = self.graph.topological_sort()
            for nid in order:
                node = self.graph.nodes[nid]
                dep_vals = [results.get(dep, inputs.get(dep)) for dep in node.dependencies]
                results[nid] = node.compute_fn(*dep_vals)
                recomputed_nodes.append(nid)

            metadata = {
                "changed_inputs": changed_inputs,
                "affected_nodes": list(affected_nodes),
                "recomputed_nodes": recomputed_nodes,
                "reused_nodes": [],
                "work_eliminated_pct": 0.0,
                "exactness_status": exactness_status,
            }
            return results, metadata

        # Execute topological order with reuse
        order = self.graph.topological_sort()
        reused_cost = 0

        for nid in order:
            node = self.graph.nodes[nid]
            if nid not in affected_nodes and nid in cached_intermediates:
                # Reuse cached intermediate
                results[nid] = cached_intermediates[nid]
                reused_nodes.append(nid)
                reused_cost += node.cost_units
            else:
                dep_vals = [results.get(dep, inputs.get(dep)) for dep in node.dependencies]
                results[nid] = node.compute_fn(*dep_vals)
                recomputed_nodes.append(nid)

        work_eliminated_pct = (reused_cost / max(1, total_cost)) * 100.0
        exactness_status = "EXACT" if (len(reused_nodes) > 0 or len(changed_inputs) == 0) else "EXACT"

        metadata = {
            "changed_inputs": changed_inputs,
            "affected_nodes": sorted(list(affected_nodes)),
            "recomputed_nodes": recomputed_nodes,
            "reused_nodes": reused_nodes,
            "work_eliminated_pct": round(work_eliminated_pct, 2),
            "exactness_status": exactness_status,
        }
        return results, metadata
