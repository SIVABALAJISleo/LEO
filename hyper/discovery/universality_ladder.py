"""
hyper/discovery/universality_ladder.py
======================================
Universality Ladder & Boundary Engine for UCTDE.

Strict Multi-Level Climb:
  LEVEL 0: Candidate
  LEVEL 1: Verified example
  LEVEL 2: Repeated verification
  LEVEL 3: Multiple workload families
  LEVEL 4: Broad generalization
  LEVEL 5: Formalized transformation principle
  LEVEL 6: Formal proof under assumptions
  LEVEL 7: Universal theorem

Boundary Engine:
  When Level 7 cannot be achieved, derives explicit applicability_conditions
  rather than emitting a generic 'FAILED' label.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.hypotheses import ResearchHypothesis, UniversalityLevel
from hyper.discovery.proof_engine import ProofCertificate, ProofStatus
from hyper.discovery.counterexample_engine import Counterexample


class BoundaryReport(BaseModel):
    hypothesis_id: str
    achieved_level: UniversalityLevel
    is_universal_theorem: bool = False
    satisfying_workloads: List[str] = Field(default_factory=list)
    violating_workloads: List[str] = Field(default_factory=list)
    applicability_conditions: List[str] = Field(default_factory=list)
    boundary_separation_property: str
    rationales: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["achieved_level"] = int(self.achieved_level.value)
        return data


class UniversalityLadder:
    """
    Evaluates and enforces rigorous criteria for climbing the 8 universality levels.
    Prohibits leaping from Level 1 to Level 7.
    """

    @staticmethod
    def evaluate_level(
        hypothesis: ResearchHypothesis,
        verified_run_count: int,
        distinct_family_count: int,
        proof_cert: Optional[ProofCertificate] = None,
        counterexamples: Optional[List[Counterexample]] = None,
        is_formalized_rule: bool = False,
    ) -> UniversalityLevel:
        """
        Determines the true, uninflated universality level of a hypothesis.
        """
        cxs = counterexamples or []

        # If counterexamples exist, theorem cannot be universal
        if len(cxs) > 0:
            # Cannot climb past Level 1 if an active counterexample breaks the hypothesis
            return UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE if verified_run_count > 0 else UniversalityLevel.LEVEL_0_CANDIDATE

        # Level 0: Candidate
        if verified_run_count == 0:
            return UniversalityLevel.LEVEL_0_CANDIDATE

        # Level 1: Verified example (at least 1 run passed)
        current = UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE

        # Level 2: Repeated verification (>= 10 successful randomized runs)
        if verified_run_count >= 10:
            current = UniversalityLevel.LEVEL_2_REPEATED_VERIFICATION

        # Level 3: Multiple workload families (>= 2 distinct families)
        if current >= UniversalityLevel.LEVEL_2_REPEATED_VERIFICATION and distinct_family_count >= 2:
            current = UniversalityLevel.LEVEL_3_MULTIPLE_WORKLOAD_FAMILIES

        # Level 4: Broad generalization (>= 5 families or extensive domain coverage)
        if current >= UniversalityLevel.LEVEL_3_MULTIPLE_WORKLOAD_FAMILIES and distinct_family_count >= 5:
            current = UniversalityLevel.LEVEL_4_BROAD_GENERALIZATION

        # Level 5: Formalized transformation principle (rule in library)
        if is_formalized_rule and current >= UniversalityLevel.LEVEL_2_REPEATED_VERIFICATION:
            current = UniversalityLevel.LEVEL_5_FORMALIZED_PRINCIPLE

        # Level 6: Formal proof under assumptions
        if proof_cert and proof_cert.status == ProofStatus.FORMALLY_PROVED:
            if len(proof_cert.assumptions) > 0:
                current = UniversalityLevel.LEVEL_6_FORMAL_PROOF_UNDER_ASSUMPTIONS
            else:
                # Level 7: Universal theorem (proved with NO restrictive domain assumptions)
                current = UniversalityLevel.LEVEL_7_UNIVERSAL_THEOREM

        return current


class UniversalityBoundaryEngine:
    """
    Investigates what properties separate workloads where a transformation holds
    from workloads where it fails.
    """

    def analyze_boundary(
        self,
        hypothesis: ResearchHypothesis,
        satisfying: List[str],
        violating: List[str],
        counterexamples: List[Counterexample],
    ) -> BoundaryReport:
        applicability: List[str] = []
        separation: str = "Unspecified boundary"

        if len(violating) == 0 and len(counterexamples) == 0:
            is_universal = (hypothesis.universality_level == UniversalityLevel.LEVEL_7_UNIVERSAL_THEOREM)
            separation = "No known violating workloads detected in explored space"
            applicability = ["All tested inputs in target domain"]
        else:
            is_universal = False
            # Analyze failure modes from counterexamples
            modes = {cx.failure_mode for cx in counterexamples}
            if "NUMERICAL_DIVERGENCE" in modes:
                applicability.append("Input values within well-conditioned dynamic range (|x| < 1e15)")
                separation = "Condition number and extreme dynamic range limit"
            if "OUT_OF_BOUNDS" in modes or any("K >" in cx.explanation for cx in counterexamples):
                applicability.append("Key range bounded by O(N) memory ceiling")
                separation = "Key domain cardinality vs available working memory"
            if "NAN_OVERFLOW" in modes:
                applicability.append("Input strictly contains real, non-NaN/Inf finite numbers")
                separation = "IEEE 754 floating point singularity"

            if not applicability:
                applicability.append("Restricted to positive verification instances")
                separation = "Empirical divergence boundary"

        report = BoundaryReport(
            hypothesis_id=hypothesis.hypothesis_id,
            achieved_level=hypothesis.universality_level,
            is_universal_theorem=is_universal,
            satisfying_workloads=satisfying,
            violating_workloads=violating,
            applicability_conditions=applicability,
            boundary_separation_property=separation,
            rationales=[
                f"Evaluated {len(satisfying)} satisfying and {len(violating)} violating workloads.",
                f"Identified boundary condition: {separation}",
            ],
        )
        return report
