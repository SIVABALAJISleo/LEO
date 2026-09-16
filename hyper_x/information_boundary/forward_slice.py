#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/forward_slice.py
=============================================
Phase 3: Forward Slicing Engine.
Starting from a set of perturbed or active input/intermediate nodes,
computes the downstream cone of influence towards observables.
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any
from .influence_graph import InfluenceGraph, InformationCategory


class ForwardSliceEngine:
    """
    Computes forward slices across computational influence graphs.
    Identifies which observables are impacted by changes to specified input/state subsets.
    """

    def __init__(self, graph: Optional[InfluenceGraph] = None):
        self.graph = graph or InfluenceGraph()

    def set_graph(self, graph: InfluenceGraph) -> None:
        self.graph = graph

    def compute_slice(self, source_node_ids: List[str]) -> Dict[str, Any]:
        """
        Extracts forward impact cone reachable from `source_node_ids`.
        """
        # Build forward adjacency
        forward_adj: Dict[str, List[str]] = {nid: [] for nid in self.graph.nodes}
        for nid, node in self.graph.nodes.items():
            for dep in node.dependencies:
                if dep in forward_adj:
                    forward_adj[dep].append(nid)

        impacted_nodes: Set[str] = set()
        frontier: List[str] = list(source_node_ids)

        for src_id in source_node_ids:
            if src_id in self.graph.nodes:
                impacted_nodes.add(src_id)

        while frontier:
            curr_id = frontier.pop(0)
            for child_id in forward_adj.get(curr_id, []):
                if child_id not in impacted_nodes:
                    impacted_nodes.add(child_id)
                    frontier.append(child_id)

        impacted_observables = [
            nid for nid in impacted_nodes if nid in self.graph.observable_ids
        ]

        total_observables = len(self.graph.observable_ids)
        total_nodes = len(self.graph.nodes)

        return {
            "source_node_ids": source_node_ids,
            "impacted_node_ids": sorted(list(impacted_nodes)),
            "impacted_node_count": len(impacted_nodes),
            "impacted_observables": sorted(impacted_observables),
            "impacted_observable_count": len(impacted_observables),
            "observable_impact_ratio": len(impacted_observables) / max(total_observables, 1) if total_observables > 0 else 0.0,
            "total_nodes": total_nodes,
        }
