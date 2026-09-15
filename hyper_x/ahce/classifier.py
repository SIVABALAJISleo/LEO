"""
hyper_x/ahce/classifier.py
==========================
Structural Workload Classifier for AHCE.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List
from .workload_signature import WorkloadSignature
from .contract import AHCEContract, CorrectnessClass


class WorkloadArchetype(str, Enum):
    EXACT_CACHE_REUSABLE = "EXACT_CACHE_REUSABLE"
    STRUCTURED_SPARSE = "STRUCTURED_SPARSE"
    INTRINSIC_LOW_RANK = "INTRINSIC_LOW_RANK"
    TEMPORAL_COHERENT = "TEMPORAL_COHERENT"
    MEMORY_BANDWIDTH_BOUND = "MEMORY_BANDWIDTH_BOUND"
    DENSE_IRREDUCIBLE = "DENSE_IRREDUCIBLE"
    PERCEPTUAL_GRAPHICS = "PERCEPTUAL_GRAPHICS"


class AHCEClassifier:
    """Classifies workloads based on measurable structural features and contract allowances."""

    def classify(
        self,
        signature: WorkloadSignature,
        contract: AHCEContract
    ) -> List[WorkloadArchetype]:
        archetypes: List[WorkloadArchetype] = []
        feat = signature.features

        # 1. Exact Cache check
        if contract.allow_cache:
            archetypes.append(WorkloadArchetype.EXACT_CACHE_REUSABLE)

        # 2. Sparsity check (Only if density < 0.35 and sparsity > 0.65)
        if feat.sparsity >= 0.65:
            archetypes.append(WorkloadArchetype.STRUCTURED_SPARSE)

        # 3. Low Rank check (Effective rank < 0.25 * min_dim and contract allows approximation or reformulation)
        min_dim = min(feat.dimensions) if feat.dimensions else 1
        if (
            feat.estimated_effective_rank is not None
            and feat.estimated_effective_rank < (min_dim * 0.30)
            and (contract.allow_approximation or contract.correctness_class in (
                CorrectnessClass.NUMERICALLY_EQUIVALENT,
                CorrectnessClass.BOUNDED_APPROXIMATION,
                CorrectnessClass.CONTRACT_EQUIVALENT
            ))
        ):
            archetypes.append(WorkloadArchetype.INTRINSIC_LOW_RANK)

        # 4. Temporal Coherence
        if feat.temporal_similarity >= 0.70:
            archetypes.append(WorkloadArchetype.TEMPORAL_COHERENT)

        # 5. Memory Bandwidth Bound
        if feat.arithmetic_intensity < 1.2:
            archetypes.append(WorkloadArchetype.MEMORY_BANDWIDTH_BOUND)

        # 6. Fallback default: Dense Irreducible
        if not archetypes or (len(archetypes) == 1 and archetypes[0] == WorkloadArchetype.EXACT_CACHE_REUSABLE):
            archetypes.append(WorkloadArchetype.DENSE_IRREDUCIBLE)

        return archetypes
