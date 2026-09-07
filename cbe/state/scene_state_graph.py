"""
cbe/state/scene_state_graph.py
Hierarchical spatial dependency graph of scene entities for subgraph invalidation.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

from .object_state import ObjectState


@dataclass
class SceneNode:
    node_id: str
    object_ref: Optional[ObjectState] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    local_transform: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))
    world_transform: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))
    bounding_box_min: np.ndarray = field(default_factory=lambda: np.array([-1, -1, -1], dtype=np.float32))
    bounding_box_max: np.ndarray = field(default_factory=lambda: np.array([1, 1, 1], dtype=np.float32))
    is_dirty: bool = False


class SceneStateGraph:
    """
    DAG representation of scene entities, allowing efficient subtree updates
    and localized spatial invalidation.
    """
    def __init__(self):
        self.nodes: Dict[str, SceneNode] = {}
        self.root_ids: List[str] = []
        self._dirty_set: Set[str] = set()

    def add_node(self, node_id: str, object_ref: Optional[ObjectState] = None, parent_id: Optional[str] = None) -> SceneNode:
        node = SceneNode(node_id=node_id, object_ref=object_ref, parent_id=parent_id)
        self.nodes[node_id] = node
        
        if parent_id is not None and parent_id in self.nodes:
            self.nodes[parent_id].children_ids.append(node_id)
        else:
            self.root_ids.append(node_id)
            
        self.mark_dirty(node_id)
        return node

    def add_edge(self, parent_id: str, child_id: str):
        """Adds a directed parent -> child edge in the scene graph."""
        if parent_id in self.nodes and child_id in self.nodes:
            if child_id not in self.nodes[parent_id].children_ids:
                self.nodes[parent_id].children_ids.append(child_id)
            self.nodes[child_id].parent_id = parent_id
            if child_id in self.root_ids:
                self.root_ids.remove(child_id)

    def mark_dirty(self, node_id: str):
        """Recursively marks node and its descendant hierarchy as dirty."""
        if node_id not in self.nodes:
            return
            
        stack = [node_id]
        while stack:
            curr_id = stack.pop()
            self._dirty_set.add(curr_id)
            if curr_id in self.nodes:
                self.nodes[curr_id].is_dirty = True
                stack.extend(self.nodes[curr_id].children_ids)

    def update_transforms(self):
        """Propagates parent transforms down through dirty paths in the DAG."""
        for root_id in self.root_ids:
            self._propagate_transform(root_id, np.eye(4, dtype=np.float32))
        self._dirty_set.clear()

    def _propagate_transform(self, node_id: str, parent_world: np.ndarray):
        node = self.nodes.get(node_id)
        if not node:
            return
            
        node.world_transform = np.matmul(parent_world, node.local_transform)
        node.is_dirty = False
        
        for child_id in node.children_ids:
            self._propagate_transform(child_id, node.world_transform)

    def get_dirty_nodes(self) -> Set[str]:
        return set(self._dirty_set)
