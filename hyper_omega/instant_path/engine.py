"""
Instant Path Engine: Implements hierarchical pattern-matching and specialization.
Loop:
NEW WORKLOAD -> PATTERN MATCH -> KNOWN THEOREM?
  YES -> INSTANT SPECIALIZATION
  NO  -> KNOWN TRANSFORMATION?
    YES -> SPECIALIZE
    NO  -> KNOWN ALGORITHM FAMILY?
      YES -> SEARCH LOCAL SPACE
      NO  -> DEEP DISCOVERY
Supports both ONLINE_EXECUTION_MODE and OFFLINE_RESEARCH_MODE.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from hyper_universal.contract_ir import ContractIR
from hyper_universal.types import ResultTaxonomy
from hyper_omega.instant_path.knowledge_graph import UniversalKnowledgeGraph, KnowledgeNode


class ExecutionMode(str, Enum):
    ONLINE_EXECUTION = "ONLINE_EXECUTION"
    OFFLINE_RESEARCH = "OFFLINE_RESEARCH"


@dataclass
class InstantPathDispatchResult:
    dispatch_path: str  # INSTANT_SPECIALIZATION, TRANSFORMATION_SPECIALIZATION, LOCAL_SEARCH, DEEP_DISCOVERY
    matched_pattern: Optional[str]
    candidate_code: Optional[str]
    status: ResultTaxonomy
    description: str


class InstantPathEngine:
    """
    Decides the lowest-overhead computational path for an incoming workload.
    Avoids expensive deep discovery when a verified theorem or pattern already exists.
    """

    def __init__(self, knowledge_graph: Optional[UniversalKnowledgeGraph] = None):
        self.knowledge_graph = knowledge_graph or UniversalKnowledgeGraph()

    def route_workload(
        self,
        pattern_signature: str,
        contract: ContractIR,
        mode: ExecutionMode = ExecutionMode.ONLINE_EXECUTION,
    ) -> InstantPathDispatchResult:
        # Step 1: Pattern Match against Knowledge Graph
        node = self.knowledge_graph.lookup_pattern(pattern_signature)

        if node is not None:
            # Step 2: Check for Known Theorem
            if node.known_theorem_id and node.verification_status == "PROVEN":
                return InstantPathDispatchResult(
                    dispatch_path="INSTANT_SPECIALIZATION",
                    matched_pattern=pattern_signature,
                    candidate_code=node.specialized_code_template,
                    status=ResultTaxonomy.TARGET_REACHED,
                    description=f"Instant specialization applied from proven theorem: {node.known_theorem_id}"
                )

            # Step 3: Check for Known Transformation
            if node.known_transformation_id:
                return InstantPathDispatchResult(
                    dispatch_path="TRANSFORMATION_SPECIALIZATION",
                    matched_pattern=pattern_signature,
                    candidate_code=node.specialized_code_template,
                    status=ResultTaxonomy.VERIFIED,
                    description=f"Specialized using known transformation: {node.known_transformation_id}"
                )

            # Step 4: Check for Known Algorithm Family
            if node.algorithm_family:
                return InstantPathDispatchResult(
                    dispatch_path="LOCAL_SEARCH",
                    matched_pattern=pattern_signature,
                    candidate_code=node.specialized_code_template,
                    status=ResultTaxonomy.FOUND,
                    description=f"Constrained local search within algorithm family: {node.algorithm_family}"
                )

        # Step 5: Deep Discovery required
        if mode == ExecutionMode.ONLINE_EXECUTION:
            # In online mode without matching pattern, cannot block indefinitely on deep discovery
            return InstantPathDispatchResult(
                dispatch_path="FALLBACK_ONLINE",
                matched_pattern=None,
                candidate_code=None,
                status=ResultTaxonomy.UNKNOWN,
                description="No matching pattern found in online mode. Falling back to reference/UNKNOWN."
            )
        else:
            # Offline research mode launches full search
            return InstantPathDispatchResult(
                dispatch_path="DEEP_DISCOVERY",
                matched_pattern=None,
                candidate_code=None,
                status=ResultTaxonomy.SEARCH_SATURATED,
                description="Initiating offline multi-strategy computational escape and deep discovery."
            )
