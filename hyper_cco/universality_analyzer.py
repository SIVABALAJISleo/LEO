"""
hyper_cco/universality_analyzer.py
=============================================================================
Universality & Scope Analyzer (Section 81)
=============================================================================
Evaluates the scientific scope and generalizability of discovered optimizations.

Scope Classes:
  1. WORKLOAD_SPECIFIC: Only works on this exact workload instance.
  2. PARAMETER_SPECIFIC: Valid only for specific parameter configurations (e.g. rank r <= 16).
  3. CONTRACT_SPECIFIC: Valid only under relaxed error tolerances (fails exact contracts).
  4. DOMAIN_SPECIFIC: Generalizes across an entire domain (e.g. all 2D PDE stencils).
  5. HARDWARE_SPECIFIC: Depends on host ISA/EU architecture (e.g. AVX2 or Intel UHD).
  6. BROADLY_GENERAL: Universal mathematical or algorithmic property.

CRITICAL INVARIANT:
Never label a workload-specific or contract-dependent optimization as UNIVERSAL.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class TransformationScope(str, enum.Enum):
    WORKLOAD_SPECIFIC = "WORKLOAD_SPECIFIC"
    PARAMETER_SPECIFIC = "PARAMETER_SPECIFIC"
    CONTRACT_SPECIFIC = "CONTRACT_SPECIFIC"
    DOMAIN_SPECIFIC = "DOMAIN_SPECIFIC"
    HARDWARE_SPECIFIC = "HARDWARE_SPECIFIC"
    BROADLY_GENERAL = "BROADLY_GENERAL"


@dataclass
class UniversalityAssessment:
    transformation_name: str
    primary_scope: TransformationScope
    applicable_domains: List[str]
    applicability_predicates: List[str]
    falsification_boundaries: List[str]
    is_universal_claim_valid: bool
    scientific_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformation_name": self.transformation_name,
            "primary_scope": self.primary_scope.value,
            "applicable_domains": self.applicable_domains,
            "applicability_predicates": self.applicability_predicates,
            "falsification_boundaries": self.falsification_boundaries,
            "is_universal_claim_valid": self.is_universal_claim_valid,
            "scientific_summary": self.scientific_summary,
        }


class UniversalityAnalyzer:
    """Classifies the valid generality of any discovered computational wormhole."""

    @staticmethod
    def assess(
        transformation_name: str,
        tested_domains: List[str],
        tested_tolerances: List[float],
        passed_exact: bool,
        spectral_dependency: bool = False
    ) -> UniversalityAssessment:
        predicates = []
        boundaries = []

        # If it fails exact contracts, it is contract-specific
        if not passed_exact:
            predicates.append("Requires contract tolerance epsilon > 0")
            boundaries.append("Fails on bit-exact or zero-tolerance contracts")
            primary_scope = TransformationScope.CONTRACT_SPECIFIC
        elif spectral_dependency:
            predicates.append("Requires intrinsic rank r << min(M, N)")
            boundaries.append("Fails on full-rank i.i.d. Gaussian or random matrices")
            primary_scope = TransformationScope.PARAMETER_SPECIFIC
        elif len(tested_domains) == 1:
            predicates.append(f"Tested only within domain '{tested_domains[0]}'")
            boundaries.append("Cross-domain transfer not empirically validated")
            primary_scope = TransformationScope.DOMAIN_SPECIFIC
        elif len(tested_domains) > 3 and passed_exact:
            predicates.append("Preserves exact mathematical equality across domains")
            boundaries.append("Bounded by memory bandwidth and hardware synchronization")
            primary_scope = TransformationScope.BROADLY_GENERAL
        else:
            primary_scope = TransformationScope.WORKLOAD_SPECIFIC

        is_universal = (primary_scope == TransformationScope.BROADLY_GENERAL)

        return UniversalityAssessment(
            transformation_name=transformation_name,
            primary_scope=primary_scope,
            applicable_domains=tested_domains,
            applicability_predicates=predicates,
            falsification_boundaries=boundaries,
            is_universal_claim_valid=is_universal,
            scientific_summary=(
                f"Transformation '{transformation_name}' is classified as {primary_scope.value}. "
                f"Universal claims are {'ALLOWED' if is_universal else 'STRICTLY PROHIBITED'}."
            )
        )
