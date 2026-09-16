#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/dependency_analyzer.py
===================================================
Phase 3: Dependency Analyzer.
Analyzes computational dependency graphs to compute reachability, transitive closures,
and causal dependency cones for any given target observable.
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any
from .influence_graph import InfluenceGraph, InfluenceNode, InformationCategory


class DependencyAnalyzer:
    """
    Computes static and dynamic dependency relations on execution graphs.
    Identifies full ancestor sets, direct dependencies, and dependency depths.
    """

    def __init__(self, graph: Optional[InfluenceGraph] = None):
        self.graph = graph or InfluenceGraph()

    def set_graph(self, graph: InfluenceGraph) -> None:
        self.graph = graph

    def get_ancestors(self, target_node_id: str) -> Set[str]:
        """Returns the set of all upstream nodes transitively required by target_node_id."""
        visited: Set[str] = set()
        queue: List[str] = [target_node_id]

        while queue:
            curr = queue.pop(0)
            if curr not in self.graph.nodes:
                continue
            node = self.graph.nodes[curr]
            for dep in node.dependencies:
                if dep not in visited:
                    visited.add(dep)
                    queue.append(dep)
        return visited

    def get_descendants(self, source_node_id: str) -> Set[str]:
        """Returns the set of all downstream nodes influenced by source_node_id."""
        visited: Set[str] = set()
        queue: List[str] = [source_node_id]

        # Build reverse adjacency map
        rev_adj: Dict[str, List[str]] = {nid: [] for nid in self.graph.nodes}
        for nid, node in self.graph.nodes.items():
            for dep in node.dependencies:
                if dep in rev_adj:
                    rev_adj[dep].append(nid)

        while queue:
            curr = queue.pop(0)
            for child in rev_adj.get(curr, []):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)
        return visited

    def compute_dependency_depth(self, node_id: str) -> int:
        """Computes critical path length (maximum dependency depth) to root inputs."""
        memo: Dict[str, int] = {}

        def _dfs(nid: str) -> int:
            if nid in memo:
                return memo[nid]
            if nid not in self.graph.nodes or not self.graph.nodes[nid].dependencies:
                memo[nid] = 0
                return 0
            max_d = 0
            for dep in self.graph.nodes[nid].dependencies:
                max_d = max(max_d, 1 + _dfs(dep))
            memo[nid] = max_d
            return max_d

        return _dfs(node_id)

    def analyze_reachability(self, targets: List[str]) -> Dict[str, Any]:
        """
        Calculates complete reachability metrics for declared target observables.
        """
        all_required: Set[str] = set(targets)
        for t in targets:
            all_required.update(self.get_ancestors(t))

        total_nodes = len(self.graph.nodes)
        required_count = len(all_required)
        dead_nodes = set(self.graph.nodes.keys()) - all_required

        return {
            "total_nodes": total_nodes,
            "required_nodes_count": required_count,
            "dead_nodes_count": len(dead_nodes),
            "reachability_ratio": required_count / max(total_nodes, 1),
            "required_node_ids": sorted(list(all_required)),
            "dead_node_ids": sorted(list(dead_nodes)),
        }
