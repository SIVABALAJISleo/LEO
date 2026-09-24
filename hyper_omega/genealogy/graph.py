"""
Candidate Genealogy and Novelty Graph:
Maintains a directed acyclic graph of candidates with multi-hash novelty,
lineage, assumptions, mutations, verification outcomes, and killing counterexamples.
"""
from dataclasses import dataclass, field
import hashlib
from typing import Any, Dict, List, Optional, Set


@dataclass
class CandidateNode:
    candidate_id: str
    parent_ids: List[str] = field(default_factory=list)
    mutation_history: List[str] = field(default_factory=list)
    crossover_history: List[str] = field(default_factory=list)
    transformation_history: List[str] = field(default_factory=list)
    representation_history: List[str] = field(default_factory=list)
    program_history: List[str] = field(default_factory=list)
    verification_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    counterexamples: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    creation_reason: str = ""

    # Multi-hash tracking (Section 19)
    structural_hash: str = ""
    mathematical_hash: str = ""
    transformation_hash: str = ""
    algorithm_hash: str = ""
    program_hash: str = ""
    representation_hash: str = ""
    execution_hash: str = ""


class CandidateGenealogyGraph:
    """
    Directed candidate graph storing complete developmental lineage.
    Enables deep causal introspection into every computational discovery.
    """

    def __init__(self):
        self.nodes: Dict[str, CandidateNode] = {}
        self.known_hashes: Set[str] = set()

    def add_candidate(self, node: CandidateNode) -> None:
        self.nodes[node.candidate_id] = node
        composite_hash = f"{node.structural_hash}:{node.mathematical_hash}:{node.algorithm_hash}"
        self.known_hashes.add(composite_hash)

    def is_novel(self, structural_hash: str, mathematical_hash: str, algorithm_hash: str) -> bool:
        """Determines if a candidate represents a genuinely new computational point."""
        composite = f"{structural_hash}:{mathematical_hash}:{algorithm_hash}"
        return composite not in self.known_hashes

    def why_created(self, candidate_id: str) -> str:
        """Answers: «Why was this candidate created?»"""
        node = self.nodes.get(candidate_id)
        if not node:
            return f"Candidate {candidate_id} not found."
        return node.creation_reason or f"Created from parents {node.parent_ids} via mutations {node.mutation_history}"

    def which_failed_candidate_led_to_it(self, candidate_id: str) -> List[str]:
        """Answers: «Which failed candidate led to it?»"""
        node = self.nodes.get(candidate_id)
        if not node:
            return []
        failed_ancestors = []
        for p_id in node.parent_ids:
            p_node = self.nodes.get(p_id)
            if p_node and p_node.counterexamples:
                failed_ancestors.append(p_id)
        return failed_ancestors

    def which_assumption_produced_improvement(self, candidate_id: str) -> List[str]:
        """Answers: «Which assumption produced the improvement?»"""
        node = self.nodes.get(candidate_id)
        if not node:
            return []
        return node.assumptions

    def which_counterexample_killed_ancestor(self, candidate_id: str) -> List[str]:
        """Answers: «Which counterexample killed its ancestor?»"""
        node = self.nodes.get(candidate_id)
        if not node:
            return []
        cx_list = []
        for p_id in node.parent_ids:
            p_node = self.nodes.get(p_id)
            if p_node and p_node.counterexamples:
                cx_list.extend(p_node.counterexamples)
        return cx_list
