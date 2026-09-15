"""
hyper_x/leaf/information_boundary.py
====================================
Information Boundary Engine for LEAF.

Determines the minimal information required by the application contract
and prunes all computation outside this boundary.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .observable import ObservableSpec, ObservableType
from .contract import LeafContract


@dataclass
class BoundaryReport:
    """Analysis of information boundary and work reduction potential."""
    original_element_count: int
    observed_element_count: int
    information_compression_ratio: float
    is_full_observation: bool
    can_prune_upstream_work: bool
    recommended_pathway: str


class InformationBoundaryEngine:
    """
    Analyzes computational observables and bounds upstream computation.
    """

    def analyze_boundary(
        self,
        state_shape: Tuple[int, ...],
        observable: ObservableSpec,
        contract: LeafContract,
    ) -> BoundaryReport:
        """Analyzes element counts and boundary compression."""
        total_elements = int(np.prod(state_shape))

        if observable.obs_type == ObservableType.FULL_TENSOR:
            observed_elements = total_elements
            ratio = 1.0
            can_prune = False
            rec = "FULL_COMPUTE_OR_FACTORIZATION"
        elif observable.obs_type == ObservableType.SCALAR_REDUCTION:
            observed_elements = 1
            ratio = float(total_elements)
            can_prune = True
            rec = "DIRECT_REDUCTION_COLLAPSE"
        elif observable.obs_type == ObservableType.ARGMAX:
            observed_elements = 1
            ratio = float(total_elements)
            can_prune = True
            rec = "BOUND_AND_PRUNE_SEARCH"
        elif observable.obs_type == ObservableType.TOP_K:
            observed_elements = min(total_elements, observable.k or 5)
            ratio = float(total_elements) / max(1, observed_elements)
            can_prune = True
            rec = "SUB_SPACE_TOPK_PRUNING"
        elif observable.obs_type == ObservableType.SUB_SLICE:
            # Estimate sliced elements
            dummy = np.zeros(state_shape, dtype=np.bool_)
            if observable.slice_indices:
                sliced = dummy[observable.slice_indices]
                observed_elements = int(sliced.size)
            else:
                observed_elements = total_elements
            ratio = float(total_elements) / max(1, observed_elements)
            can_prune = observed_elements < total_elements
            rec = "SLICE_ONLY_EVALUATION"
        elif observable.obs_type == ObservableType.SAMPLE_POINTS:
            coords = observable.sample_coordinates
            observed_elements = len(coords) if coords is not None else total_elements
            ratio = float(total_elements) / max(1, observed_elements)
            can_prune = True
            rec = "NEURAL_OR_IMPLICIT_FIELD_QUERY"
        else:
            observed_elements = total_elements
            ratio = 1.0
            can_prune = False
            rec = "STANDARD_EXECUTION"

        return BoundaryReport(
            original_element_count=total_elements,
            observed_element_count=observed_elements,
            information_compression_ratio=ratio,
            is_full_observation=(observed_elements == total_elements),
            can_prune_upstream_work=can_prune,
            recommended_pathway=rec,
        )
