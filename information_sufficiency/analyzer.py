"""
information_sufficiency/analyzer.py
Classifies computational graph nodes into seven sufficiency categories,
providing formal mathematical justifications for why work can be legally eliminated.
"""

from enum import Enum
from typing import Dict, Any, List, Set, Optional
import numpy as np


class SufficiencyClass(str, Enum):
    """Classification of an operation or tensor's relevance to the contract."""
    ESSENTIAL = "ESSENTIAL"                             # Directly affects output within tight contract bounds
    CONDITIONALLY_ESSENTIAL = "CONDITIONALLY_ESSENTIAL" # Affects output only under specific input regimes
    REDUNDANT = "REDUNDANT"                             # Identical or algebraically equivalent to an existing result
    DERIVABLE = "DERIVABLE"                             # Can be computed via a lower-cost exact/bounded transform
    PREDICTABLE = "PREDICTABLE"                         # High confidence prediction verifiable via cheap spot checks
    DISCARDABLE = "DISCARDABLE"                         # Has zero influence on contract-specified consumed outputs
    UNKNOWN = "UNKNOWN"                                 # Requires further profiling or conservative retention


class SufficiencyDecision:
    """Detailed record of a sufficiency classification."""
    def __init__(
        self,
        node_id: str,
        classification: SufficiencyClass,
        justification: str,
        elimination_potential: float,  # 0.0 to 1.0
        replacement_strategy: Optional[str] = None
    ):
        self.node_id = node_id
        self.classification = classification
        self.justification = justification
        self.elimination_potential = elimination_potential
        self.replacement_strategy = replacement_strategy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "classification": self.classification.value,
            "justification": self.justification,
            "elimination_potential": self.elimination_potential,
            "replacement_strategy": self.replacement_strategy
        }


class InformationSufficiencyAnalyzer:
    """Analyzes computational requirements to determine minimum sufficient information."""

    @staticmethod
    def classify_node(
        node_name: str,
        op_type: str,
        input_shapes: List[List[int]],
        output_shape: List[int],
        consumed_indices: Optional[List[int]] = None,
        is_linear: bool = True,
        is_downstream_active: bool = True,
        cached_equivalent_available: bool = False
    ) -> SufficiencyDecision:
        """Determines the sufficiency status of a given operation."""
        # 1. Check if output is not consumed downstream
        if not is_downstream_active:
            return SufficiencyDecision(
                node_id=node_name,
                classification=SufficiencyClass.DISCARDABLE,
                justification="Output has zero downstream consumers in the active execution graph.",
                elimination_potential=1.0,
                replacement_strategy="dead_code_elimination"
            )

        # 2. Check if identical result is already cached
        if cached_equivalent_available:
            return SufficiencyDecision(
                node_id=node_name,
                classification=SufficiencyClass.REDUNDANT,
                justification="Exact or contract-equivalent output already exists in cache hierarchy.",
                elimination_potential=1.0,
                replacement_strategy="cache_lookup"
            )

        # 3. Check for partial consumption (e.g. top-k, region of interest, single element)
        if consumed_indices is not None and len(consumed_indices) > 0:
            total_elements = int(np.prod(output_shape))
            consumed_ratio = len(consumed_indices) / max(total_elements, 1)
            if consumed_ratio < 0.2:
                return SufficiencyDecision(
                    node_id=node_name,
                    classification=SufficiencyClass.DERIVABLE,
                    justification=f"Only {consumed_ratio*100:.2f}% of output elements are consumed downstream.",
                    elimination_potential=1.0 - consumed_ratio,
                    replacement_strategy="output_aware_strided_evaluation"
                )

        # 4. Check for linear algebraic simplifications
        if is_linear and op_type in ["matmul", "gemm", "projection"]:
            # Matrix operations are derivable if low rank or structured
            return SufficiencyDecision(
                node_id=node_name,
                classification=SufficiencyClass.CONDITIONALLY_ESSENTIAL,
                justification="Linear operator suitable for low-rank SVD or 2:4 structured sparsity under contract.",
                elimination_potential=0.5,
                replacement_strategy="low_rank_or_sparse_factorization"
            )

        # Default fallback
        return SufficiencyDecision(
            node_id=node_name,
            classification=SufficiencyClass.ESSENTIAL,
            justification="Full computation is required to guarantee contract correctness.",
            elimination_potential=0.0,
            replacement_strategy=None
        )

    @staticmethod
    def audit_graph_sufficiency(nodes_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits an entire graph of nodes and produces an overall sufficiency profile."""
        decisions: List[SufficiencyDecision] = []
        total_elimination_potential = 0.0

        for node in nodes_info:
            decision = InformationSufficiencyAnalyzer.classify_node(
                node_name=node.get("name", "unknown"),
                op_type=node.get("op_type", "generic"),
                input_shapes=node.get("input_shapes", []),
                output_shape=node.get("output_shape", [1]),
                consumed_indices=node.get("consumed_indices", None),
                is_linear=node.get("is_linear", True),
                is_downstream_active=node.get("is_downstream_active", True),
                cached_equivalent_available=node.get("cached_available", False)
            )
            decisions.append(decision)
            total_elimination_potential += decision.elimination_potential

        mean_potential = total_elimination_potential / max(len(decisions), 1)
        return {
            "total_nodes_analyzed": len(decisions),
            "mean_elimination_potential": mean_potential,
            "decisions": [d.to_dict() for d in decisions],
            "discardable_count": sum(1 for d in decisions if d.classification == SufficiencyClass.DISCARDABLE),
            "redundant_count": sum(1 for d in decisions if d.classification == SufficiencyClass.REDUNDANT),
            "derivable_count": sum(1 for d in decisions if d.classification == SufficiencyClass.DERIVABLE),
            "essential_count": sum(1 for d in decisions if d.classification == SufficiencyClass.ESSENTIAL)
        }
