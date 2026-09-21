"""
hyper/discovery/knowledge_graph.py
==================================
Computational Knowledge Graph for UCTDE.

Represents scientific discovery trajectories:
  Hypothesis -> Transformation -> Experiment -> Verification -> Result -> Counterexample -> Refined Hypothesis
"""

from __future__ import annotations
import uuid
import time
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    WORKLOAD = "WORKLOAD"
    HYPOTHESIS = "HYPOTHESIS"
    PATHWAY = "PATHWAY"
    EXPERIMENT = "EXPERIMENT"
    VERIFICATION = "VERIFICATION"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    RULE = "RULE"


class EdgeType(str, Enum):
    INVESTIGATES = "INVESTIGATES"             # Hypothesis -> Workload
    PROPOSES_PATHWAY = "PROPOSES_PATHWAY"     # Hypothesis -> Pathway
    APPLIES_TRANSFORMATION = "APPLIES"       # Pathway -> Rule / Transformation
    EVALUATED_IN = "EVALUATED_IN"             # Pathway -> Experiment
    VERIFIED_BY = "VERIFIED_BY"               # Experiment -> Verification
    CONTRADICTED_BY = "CONTRADICTED_BY"       # Hypothesis -> Counterexample
    PROVES = "PROVES"                         # Verification -> Hypothesis
    REFINES = "REFINES"                       # RefinedHypothesis -> ParentHypothesis
    ABSTRACTS_TO = "ABSTRACTS_TO"             # Pathway -> Rule


class KnowledgeNode(BaseModel):
    node_id: str
    node_type: NodeType
    label: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["node_type"] = self.node_type.value
        return data


class KnowledgeEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: f"edge-{uuid.uuid4().hex[:8]}")
    source_id: str
    target_id: str
    edge_type: EdgeType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["edge_type"] = self.edge_type.value
        return data


class ComputationalKnowledgeGraph:
    """
    In-memory and persistent graph representing all hypotheses, experiments,
    proofs, counterexamples, and rules discovered by UCTDE.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self._adjacency: Dict[str, Set[str]] = {}
        self._reverse_adjacency: Dict[str, Set[str]] = {}

    def add_node(self, node_id: str, node_type: NodeType, label: str, **attributes: Any) -> KnowledgeNode:
        if node_id in self.nodes:
            self.nodes[node_id].label = label
            self.nodes[node_id].attributes.update(attributes)
            return self.nodes[node_id]

        node = KnowledgeNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            attributes=attributes,
        )
        self.nodes[node_id] = node
        self._adjacency[node_id] = set()
        self._reverse_adjacency[node_id] = set()
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, **metadata: Any) -> KnowledgeEdge:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise KeyError(f"Both nodes must exist before adding edge: {source_id} -> {target_id}")

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            metadata=metadata,
        )
        self.edges[edge.edge_id] = edge
        self._adjacency[source_id].add(edge.edge_id)
        self._reverse_adjacency[target_id].add(edge.edge_id)
        return edge

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self.nodes.get(node_id)

    def get_outgoing_edges(self, node_id: str) -> List[KnowledgeEdge]:
        edge_ids = self._adjacency.get(node_id, set())
        return [self.edges[eid] for eid in edge_ids if eid in self.edges]

    def get_incoming_edges(self, node_id: str) -> List[KnowledgeEdge]:
        edge_ids = self._reverse_adjacency.get(node_id, set())
        return [self.edges[eid] for eid in edge_ids if eid in self.edges]

    def get_neighbors(self, node_id: str) -> List[KnowledgeNode]:
        outgoing = self.get_outgoing_edges(node_id)
        return [self.nodes[e.target_id] for e in outgoing if e.target_id in self.nodes]

    def find_nodes_by_type(self, node_type: NodeType) -> List[KnowledgeNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges.values()],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> ComputationalKnowledgeGraph:
        graph = cls()
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for nd in data.get("nodes", []):
            graph.add_node(
                node_id=nd["node_id"],
                node_type=NodeType(nd["node_type"]),
                label=nd["label"],
                **nd.get("attributes", {}),
            )
        for ed in data.get("edges", []):
            graph.add_edge(
                source_id=ed["source_id"],
                target_id=ed["target_id"],
                edge_type=EdgeType(ed["edge_type"]),
                **ed.get("metadata", {}),
            )
        return graph
