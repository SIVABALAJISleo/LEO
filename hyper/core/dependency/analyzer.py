"""
hyper/core/dependency/analyzer.py
Dependency analysis, def-use chains, alias tracking, and backward/forward slicing.
"""
from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional
from hyper.core.semantic_ir.models import CanonicalSemanticIR, SemanticNode


class DependencyEdge:
    def __init__(self, source_id: str, target_id: str, is_control: bool = False, alias_risk: bool = False):
        self.source_id = source_id
        self.target_id = target_id
        self.is_control = is_control
        self.alias_risk = alias_risk


class DataDependencyGraph:
    """
    Explicit Data & Control Dependency Graph over Semantic IR.
    """
    def __init__(self, ir: CanonicalSemanticIR):
        self.ir = ir
        self.forward_edges: Dict[str, List[DependencyEdge]] = {k: [] for k in ir.nodes}
        self.backward_edges: Dict[str, List[DependencyEdge]] = {k: [] for k in ir.nodes}
        self._build_graph()

    def _build_graph(self):
        for node_id, node in self.ir.nodes.items():
            for inp_id in node.inputs:
                if inp_id in self.ir.nodes:
                    edge = DependencyEdge(source_id=inp_id, target_id=node_id)
                    self.forward_edges[inp_id].append(edge)
                    self.backward_edges[node_id].append(edge)

    def get_forward_dependents(self, node_id: str) -> Set[str]:
        """All nodes that transitively depend on node_id."""
        visited: Set[str] = set()
        queue = [node_id]
        while queue:
            curr = queue.pop(0)
            for edge in self.forward_edges.get(curr, []):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append(edge.target_id)
        return visited

    def get_backward_dependencies(self, node_id: str) -> Set[str]:
        """All nodes that node_id transitively depends upon."""
        visited: Set[str] = set()
        queue = [node_id]
        while queue:
            curr = queue.pop(0)
            for edge in self.backward_edges.get(curr, []):
                if edge.source_id not in visited:
                    visited.add(edge.source_id)
                    queue.append(edge.source_id)
        return visited

    def does_input_affect_output(self, input_id: str, output_id: str) -> bool:
        """Determines if mutating input_id can mathematically affect output_id."""
        return output_id in self.get_forward_dependents(input_id)

    def find_independent_subgraphs(self) -> List[List[str]]:
        """Identifies parallelizable node groups that share no mutual dependencies."""
        unvisited = set(self.ir.nodes.keys())
        subgraphs = []
        while unvisited:
            seed = next(iter(unvisited))
            connected = {seed} | self.get_forward_dependents(seed) | self.get_backward_dependencies(seed)
            subgraphs.append(sorted(list(connected & unvisited)))
            unvisited -= connected
        return subgraphs
