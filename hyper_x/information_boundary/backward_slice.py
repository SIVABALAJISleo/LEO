#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/backward_slice.py
==============================================
Phase 3: Backward Slicing Engine.
Starting from designated observable nodes, traverses dependencies in reverse to extract
the minimal causal computational slice. Unreachable operations are pruned completely.
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any
from .influence_graph import InfluenceGraph, InfluenceNode, InformationCategory


class BackwardSliceEngine:
    """
    Computes precise backward slices across computational influence graphs.
    Guarantees that no necessary operation is pruned.
    """

    def __init__(self, graph: Optional[InfluenceGraph] = None):
        self.graph = graph or InfluenceGraph()

    def set_graph(self, graph: InfluenceGraph) -> None:
        self.graph = graph

    def compute_slice(self, observable_ids: List[str]) -> Dict[str, Any]:
        """
        Extracts minimal backward slice required to compute all observables in `observable_ids`.
        """
        slice_nodes: Set[str] = set()
        slice_dependencies: Dict[str, List[str]] = {}
        frontier: List[str] = list(observable_ids)

        for obs_id in observable_ids:
            if obs_id in self.graph.nodes:
                slice_nodes.add(obs_id)

        while frontier:
            curr_id = frontier.pop(0)
            if curr_id not in self.graph.nodes:
                continue
            curr_node = self.graph.nodes[curr_id]
            slice_dependencies[curr_id] = list(curr_node.dependencies)

            for dep_id in curr_node.dependencies:
                if dep_id not in slice_nodes:
                    slice_nodes.add(dep_id)
                    frontier.append(dep_id)

        all_node_ids = set(self.graph.nodes.keys())
        pruned_nodes = all_node_ids - slice_nodes

        pruned_categories = {}
        for pid in pruned_nodes:
            pruned_categories[pid] = InformationCategory.REDUNDANT_INFORMATION.value

        return {
            "slice_node_ids": sorted(list(slice_nodes)),
            "slice_size": len(slice_nodes),
            "original_size": len(all_node_ids),
            "pruned_node_ids": sorted(list(pruned_nodes)),
            "pruned_count": len(pruned_nodes),
            "pruning_ratio": len(pruned_nodes) / max(len(all_node_ids), 1),
            "observable_targets": observable_ids,
            "is_complete_slice": True,
        }
