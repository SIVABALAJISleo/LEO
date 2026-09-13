#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/influence_graph.py
===============================================
Causal dependency graph and information partition representation.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional


class InformationCategory(str, enum.Enum):
    """Categorization of input or intermediate information relative to the observable."""
    REQUIRED_INFORMATION = "REQUIRED_INFORMATION"
    OPTIONAL_INFORMATION = "OPTIONAL_INFORMATION"
    REDUNDANT_INFORMATION = "REDUNDANT_INFORMATION"
    UNKNOWN_INFORMATION = "UNKNOWN_INFORMATION"


@dataclass
class InfluenceNode:
    node_id: str
    category: InformationCategory
    shape: Optional[List[int]] = None
    influence_score: float = 1.0     # [0.0, 1.0] where 0.0 is zero influence on target observable
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class InfluenceGraph:
    """Directed acyclic graph tracing causal influence from inputs to observables."""

    def __init__(self):
        self.nodes: Dict[str, InfluenceNode] = {}
        self.observable_ids: Set[str] = set()

    def add_node(
        self,
        node_id: str,
        category: InformationCategory = InformationCategory.REQUIRED_INFORMATION,
        shape: Optional[List[int]] = None,
        influence_score: float = 1.0,
        dependencies: Optional[List[str]] = None,
        is_observable: bool = False
    ) -> InfluenceNode:
        node = InfluenceNode(
            node_id=node_id,
            category=category,
            shape=shape,
            influence_score=influence_score,
            dependencies=dependencies or []
        )
        self.nodes[node_id] = node
        if is_observable:
            self.observable_ids.add(node_id)
        return node

    def prune_irrelevant_information(self) -> Dict[str, List[str]]:
        """
        Backward graph traversal from target observables to classify
        which nodes directly or indirectly influence the output.
        """
        visited: Set[str] = set()
        queue = list(self.observable_ids)

        while queue:
            curr = queue.pop(0)
            if curr not in visited and curr in self.nodes:
                visited.add(curr)
                queue.extend(self.nodes[curr].dependencies)

        partition = {
            "required": [],
            "redundant": [],
            "optional": [],
            "unknown": []
        }

        for node_id, node in self.nodes.items():
            if node_id in visited:
                node.category = InformationCategory.REQUIRED_INFORMATION
                partition["required"].append(node_id)
            else:
                node.category = InformationCategory.REDUNDANT_INFORMATION
                node.influence_score = 0.0
                partition["redundant"].append(node_id)

        return partition
