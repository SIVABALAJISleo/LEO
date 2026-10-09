"""
hyper/parity_engine/knowledge_graph.py
======================================
Discovery Knowledge Graph & Failure Learning Engine.
Implements Sections 36 and 37 of the HYPER 100% Master Mission.

Stores full semantic relationships between:
- GPU capability
- Workload
- Algorithm
- Transformation
- Pathway
- Certificate
- Counterexample
- Benchmark
- Failure
- Success
- Hardware constraint
- Application

Failure Memory:
Records every failed pathway, counterexample, and contract violation to prevent
the discovery engine from repeatedly exploring identical failing regions.
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FailureRecord(BaseModel):
    failure_id: str = Field(default_factory=lambda: f"FAIL_{uuid.uuid4().hex[:8]}")
    pathway_id: str
    workload_id: str
    failure_type: str  # "CONTRACT_VIOLATION", "NUMERICAL_INSTABILITY", "ADVERSARIAL_CRASH", "TIMEOUT"
    counterexample: Dict[str, Any] = Field(default_factory=dict)
    violated_contract: str
    performance_failure: bool = False
    correctness_failure: bool = True
    lesson: str
    future_constraints: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)

    def to_yaml_dict(self) -> Dict[str, Any]:
        return {
            "failure": {
                "id": self.failure_id,
                "pathway": self.pathway_id,
                "workload": self.workload_id,
                "failure_type": self.failure_type,
                "counterexample": self.counterexample,
                "violated_contract": self.violated_contract,
                "performance_failure": self.performance_failure,
                "correctness_failure": self.correctness_failure,
                "lesson": self.lesson,
                "future_constraints": self.future_constraints,
            }
        }


class DiscoveryNode(BaseModel):
    node_id: str
    node_type: str  # "CAPABILITY", "PATHWAY", "TRANSFORMATION", "CERTIFICATE", "FAILURE", "APPLICATION"
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class DiscoveryEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: str  # "IMPLEMENTS", "PROVES", "VIOLATES", "DERIVED_FROM", "COMPOSED_WITH"
    weight: float = 1.0


class DiscoveryKnowledgeGraph:
    """
    Searchable graph of all computational discoveries, verified pathways, and failure memories.
    """

    def __init__(self, db_path: str = "reports/parity_knowledge_graph.json") -> None:
        self.db_path = db_path
        self.nodes: Dict[str, DiscoveryNode] = {}
        self.edges: List[DiscoveryEdge] = []
        self.failures: Dict[str, FailureRecord] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for n in data.get("nodes", []):
                        node = DiscoveryNode(**n)
                        self.nodes[node.node_id] = node
                    for e in data.get("edges", []):
                        self.edges.append(DiscoveryEdge(**e))
                    for fl in data.get("failures", []):
                        f_rec = FailureRecord(**fl)
                        self.failures[f_rec.failure_id] = f_rec
            except Exception:
                pass

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        payload = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_failures": len(self.failures),
            "updated_at": time.time(),
            "nodes": [n.model_dump() for n in self.nodes.values()],
            "edges": [e.model_dump() for e in self.edges],
            "failures": [f.model_dump() for f in self.failures.values()],
        }
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def record_failure(
        self,
        pathway_id: str,
        workload_id: str,
        failure_type: str,
        lesson: str,
        counterexample: Optional[Dict[str, Any]] = None,
        violated_contract: str = "DEFAULT_CONTRACT",
        constraints: Optional[List[str]] = None,
    ) -> FailureRecord:
        rec = FailureRecord(
            pathway_id=pathway_id,
            workload_id=workload_id,
            failure_type=failure_type,
            counterexample=counterexample or {},
            violated_contract=violated_contract,
            lesson=lesson,
            future_constraints=constraints or [],
        )
        self.failures[rec.failure_id] = rec

        # Add node & edge to graph
        self.add_node(rec.failure_id, "FAILURE", f"Fail: {failure_type}", {"lesson": lesson})
        self.add_edge(pathway_id, rec.failure_id, "PRODUCED_FAILURE")
        self.save()
        return rec

    def add_node(self, node_id: str, node_type: str, label: str, properties: Optional[Dict[str, Any]] = None) -> None:
        self.nodes[node_id] = DiscoveryNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            properties=properties or {},
        )

    def add_edge(self, source_id: str, target_id: str, relationship: str, weight: float = 1.0) -> None:
        self.edges.append(
            DiscoveryEdge(source_id=source_id, target_id=target_id, relationship=relationship, weight=weight)
        )

    def is_region_forbidden(self, transformation_names: List[str]) -> Tuple[bool, str]:
        """
        Queries failure memory to see if this transformation set contains known fatal combinations.
        """
        for fl in self.failures.values():
            for c in fl.future_constraints:
                for tx in transformation_names:
                    if tx.lower() in c.lower():
                        return True, f"Pruned by failure memory {fl.failure_id}: {fl.lesson}"
        return False, ""
