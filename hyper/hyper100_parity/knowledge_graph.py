"""
hyper/hyper100_parity/knowledge_graph.py
=========================================
Failure Learning, Knowledge Graph & Cross-Domain Discovery (Sections 36, 37, 38).

Features:
1. Failure Learning (Section 36):
   Schema:
     failure:
       pathway_id:
       workload:
       failure_type:
       counterexample:
       violated_contract:
       performance_failure:
       correctness_failure:
       lesson:
       future_constraints:
   Prunes failed search space to prevent repeating identical failed explorations.

2. Discovery Knowledge Graph (Section 37):
   Multi-relational graph storing entities and directed relations across:
   - GPU Capability
   - Workload
   - Algorithm
   - Transformation
   - Pathway
   - Certificate
   - Counterexample
   - Benchmark
   - Success / Failure
   - Application

3. Cross-Domain Discovery Transfer (Section 38):
   Transfers principles across domains:
   - Graphics → Temporal dirty-region reuse
   - Compression → Memory representation reduction
   - Scientific computing → Sparsity & Action-reaction symmetry
   - Database systems → Incremental computation & Delta updates
   - Signal processing → FFT Convolution theorem & OMP reconstruction
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .taxonomy import CapabilityFamily


class FailureRecord(BaseModel):
    failure_id: str = Field(default_factory=lambda: f"fail-{uuid.uuid4().hex[:6]}")
    pathway_id: str
    workload: str
    failure_type: str  # NUMERICAL_DIVERGENCE, TIMEOUT, MEMORY_EXCEEDED, HOSTILE_COUNTEREXAMPLE
    counterexample_summary: str
    violated_contract: str
    performance_failure: bool = False
    correctness_failure: bool = True
    lesson: str
    future_constraints: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class CrossDomainTransfer(BaseModel):
    source_domain: CapabilityFamily
    target_domain: CapabilityFamily
    core_principle: str
    example_transformation: str
    mathematical_basis: str


class DiscoveryKnowledgeGraph:
    """
    Searchable graph storing discoveries, lessons, certificates, and cross-domain analogies.
    """

    CROSS_DOMAIN_CATALOG: List[CrossDomainTransfer] = [
        CrossDomainTransfer(
            source_domain=CapabilityFamily.GRAPHICS,
            target_domain=CapabilityFamily.VIDEO,
            core_principle="Temporal Coherence & Dirty-Region Tracking",
            example_transformation="dirty_region_bounding_box",
            mathematical_basis="Delta(Frame) has compact spatial support; only redraw modified bounding box.",
        ),
        CrossDomainTransfer(
            source_domain=CapabilityFamily.COMPRESSION,
            target_domain=CapabilityFamily.MEMORY_BEHAVIOR,
            core_principle="Delta Residual State Reduction",
            example_transformation="vectorized_run_length_delta",
            mathematical_basis="Minimize information movement across UMA bus via discrete first-difference encoding.",
        ),
        CrossDomainTransfer(
            source_domain=CapabilityFamily.SCIENTIFIC,
            target_domain=CapabilityFamily.AI_ML,
            core_principle="Rank-1 Separable Decomposition",
            example_transformation="rank_1_separable_convolution",
            mathematical_basis="2D Conv kernel K = u (x) v^T converts O(K^2) into O(2K) separable passes.",
        ),
        CrossDomainTransfer(
            source_domain=CapabilityFamily.GENERAL_COMPUTE,
            target_domain=CapabilityFamily.AI_ML,
            core_principle="Online Tree Reductions & Flash Normalization",
            example_transformation="online_softmax_tree_reduction",
            mathematical_basis="Numerically stable online softmax maintains running max without materializing N x N matrix.",
        ),
    ]

    def __init__(self, storage_path: str = "reports/hyper_knowledge_graph.json") -> None:
        self.storage_path = storage_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, str]] = []
        self.failures: List[FailureRecord] = []
        self._load()

    def record_failure(self, failure: FailureRecord) -> None:
        self.failures.append(failure)
        self.add_node(failure.failure_id, "FAILURE", failure.model_dump())
        self.add_edge(failure.pathway_id, failure.failure_id, "TERMINATED_IN")
        self.save()

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any]) -> None:
        self.nodes[node_id] = {"id": node_id, "type": node_type, "attrs": attributes}

    def add_edge(self, source_id: str, target_id: str, relation: str) -> None:
        self.edges.append({"source": source_id, "target": target_id, "relation": relation})

    def is_region_constrained(self, proposed_transformations: List[str]) -> Tuple[bool, Optional[str]]:
        """Checks if a proposed set of transformations has already been proved to fail."""
        for fail in self.failures:
            for constraint in fail.future_constraints:
                if constraint in proposed_transformations:
                    return True, f"Blocked by prior failure {fail.failure_id}: {fail.lesson}"
        return False, None

    def get_cross_domain_suggestions(self, target_domain: CapabilityFamily) -> List[CrossDomainTransfer]:
        return [t for t in self.CROSS_DOMAIN_CATALOG if t.target_domain == target_domain]

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "failure_count": len(self.failures),
            "failures": [f.model_dump() for f in self.failures],
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for f_dict in data.get("failures", []):
                        self.failures.append(FailureRecord(**f_dict))
            except Exception:
                pass
