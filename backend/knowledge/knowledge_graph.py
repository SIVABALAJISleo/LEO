"""
backend/knowledge/knowledge_graph.py
Subsystem 6: Knowledge Graph Engine.
Dynamic entity-relationship graph with O(1) indexed node lookup.
Supports symbolic reasoning via graph traversal.
"""

import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class Entity:
    """A node in the knowledge graph."""
    __slots__ = ("entity_id", "label", "entity_type", "properties", "created_at")

    def __init__(self, entity_id: str, label: str, entity_type: str = "GENERIC", properties: Dict = None):
        self.entity_id = entity_id
        self.label = label
        self.entity_type = entity_type
        self.properties = properties or {}
        self.created_at = time.time()


class Relation:
    """A directed, labeled edge between two entities."""
    __slots__ = ("source_id", "target_id", "relation_type", "weight", "properties")

    def __init__(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0, properties: Dict = None):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.weight = weight
        self.properties = properties or {}


class KnowledgeGraph:
    """
    Dynamic in-memory knowledge graph with O(1) entity lookup.
    Supports:
    - Entity/relation insertion
    - 1-hop and multi-hop traversal
    - BFS shortest-path reasoning
    - Incremental updates
    """
    def __init__(self):
        # O(1) entity lookup by ID
        self.entities: Dict[str, Entity] = {}
        # Adjacency list: source_id -> list of Relation
        self.adj: Dict[str, List[Relation]] = defaultdict(list)
        # Reverse index for target-side lookups
        self.radj: Dict[str, List[Relation]] = defaultdict(list)
        # Entity type index: type -> set of entity_ids
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
        # Label -> entity_id for fast label lookups
        self.label_index: Dict[str, str] = {}

    def add_entity(self, entity_id: str, label: str, entity_type: str = "GENERIC",
                   properties: Dict = None) -> Entity:
        entity = Entity(entity_id, label, entity_type, properties)
        self.entities[entity_id] = entity
        self.type_index[entity_type].add(entity_id)
        self.label_index[label.lower()] = entity_id
        return entity

    def add_relation(self, source_id: str, target_id: str, relation_type: str,
                     weight: float = 1.0, properties: Dict = None) -> Optional[Relation]:
        if source_id not in self.entities or target_id not in self.entities:
            logger.warning(f"Cannot add relation: entity not found ({source_id} or {target_id})")
            return None
        rel = Relation(source_id, target_id, relation_type, weight, properties)
        self.adj[source_id].append(rel)
        self.radj[target_id].append(rel)
        return rel

    def get_entity_by_label(self, label: str) -> Optional[Entity]:
        """O(1) label-to-entity lookup."""
        eid = self.label_index.get(label.lower())
        return self.entities.get(eid) if eid else None

    def get_neighbors(self, entity_id: str, relation_type: str = None) -> List[Tuple[Entity, Relation]]:
        """Returns all direct neighbors of an entity."""
        results = []
        for rel in self.adj.get(entity_id, []):
            if relation_type and rel.relation_type != relation_type:
                continue
            neighbor = self.entities.get(rel.target_id)
            if neighbor:
                results.append((neighbor, rel))
        return results

    def bfs_path(self, source_id: str, target_id: str, max_hops: int = 4) -> Optional[List[str]]:
        """
        BFS shortest-path reasoning between two entities.
        Returns list of entity IDs forming the path, or None if no path found within max_hops.
        """
        if source_id not in self.entities or target_id not in self.entities:
            return None
        if source_id == target_id:
            return [source_id]

        visited: Set[str] = {source_id}
        queue: deque = deque([(source_id, [source_id])])

        while queue:
            current_id, path = queue.popleft()
            if len(path) > max_hops:
                break
            for neighbor, _ in self.get_neighbors(current_id):
                nid = neighbor.entity_id
                if nid == target_id:
                    return path + [nid]
                if nid not in visited:
                    visited.add(nid)
                    queue.append((nid, path + [nid]))
        return None

    def infer_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Returns structured facts about an entity by traversing its 1-hop neighborhood.
        """
        facts = []
        for neighbor, rel in self.get_neighbors(entity_id):
            facts.append({
                "subject": self.entities[entity_id].label,
                "predicate": rel.relation_type,
                "object": neighbor.label,
                "weight": rel.weight
            })
        return facts

    def stats(self) -> Dict[str, int]:
        return {
            "entity_count": len(self.entities),
            "relation_count": sum(len(v) for v in self.adj.values()),
            "type_count": len(self.type_index)
        }
