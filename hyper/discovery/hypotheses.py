"""
hyper/discovery/hypotheses.py
=============================
Formal Research Hypothesis and Epistemic State Management for UCTDE.

Strict Epistemic Separation:
  TARGET != PROVEN FACT.
  States: TARGET, HYPOTHESIS, EXPERIMENT, EVIDENCE, PROOF, COUNTEREXAMPLE, UNKNOWN.
  Never collapse these into a single state.
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EpistemicState(str, Enum):
    """Rigorous epistemic state tracking. No state collapsing permitted."""
    TARGET = "TARGET"                         # Ultimate aspiration (not proven)
    HYPOTHESIS = "HYPOTHESIS"                 # Proposed statement to be investigated
    EXPERIMENT = "EXPERIMENT"                 # Active empirical test in progress
    EVIDENCE = "EVIDENCE"                     # Empirical observation (not general proof)
    PROOF = "PROOF"                           # Mathematically verified under explicit assumptions
    COUNTEREXAMPLE = "COUNTEREXAMPLE"         # Adversarial instance that breaks the hypothesis
    UNKNOWN = "UNKNOWN"                       # Inconclusive/epistemic uncertainty (mandatory default)


class UniversalityLevel(int, Enum):
    """8-step Universality Ladder."""
    LEVEL_0_CANDIDATE = 0                     # Untested candidate transformation
    LEVEL_1_VERIFIED_EXAMPLE = 1              # Passed single verification instance
    LEVEL_2_REPEATED_VERIFICATION = 2         # Passed repeated randomized trials
    LEVEL_3_MULTIPLE_WORKLOAD_FAMILIES = 3    # Verified across multiple distinct workload domains
    LEVEL_4_BROAD_GENERALIZATION = 4          # Generalized across parameterized workload families
    LEVEL_5_FORMALIZED_PRINCIPLE = 5          # Abstracted into formal transformation rule
    LEVEL_6_FORMAL_PROOF_UNDER_ASSUMPTIONS = 6# Proved mathematically under declared preconditions
    LEVEL_7_UNIVERSAL_THEOREM = 7             # Proved universally for all workloads in target domain


class TargetStatus(BaseModel):
    """Tracks current status of the ultimate destination without false claims."""
    destination: str = "Universal RTX-5090-class computational parity on CPU+iGPU"
    epistemic_state: EpistemicState = EpistemicState.TARGET
    hardware_parity_achieved: bool = False  # Strictly False (physically disjoint silicon)
    contract_parity_achieved: bool = False  # True only when verified across all tested workloads
    verified_workload_count: int = 0
    counterexample_count: int = 0
    proofs_established_count: int = 0
    unknown_regions_count: int = 0
    current_assessment: str = "Active empirical search and proof investigation"
    timestamp: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ResearchHypothesis(BaseModel):
    """
    Formal mathematical representation of a research hypothesis:
      H: ∀ W ∈ W_domain, ∃ P: Verify(P(W), C_W) = TRUE ∧ Cost(P(W)) <= Cost_target(W)
    """
    hypothesis_id: str = Field(default_factory=lambda: f"hyp-{uuid.uuid4().hex[:8]}")
    title: str
    formal_statement: str
    target_domain: str                        # e.g., "NUMERICAL_POLYNOMIAL", "SORTING", "UNIVERSAL"
    assumptions: List[str] = Field(default_factory=list)
    epistemic_state: EpistemicState = EpistemicState.HYPOTHESIS
    universality_level: UniversalityLevel = UniversalityLevel.LEVEL_0_CANDIDATE
    evidence_ids: List[str] = Field(default_factory=list)
    counterexample_ids: List[str] = Field(default_factory=list)
    proof_ids: List[str] = Field(default_factory=list)
    applicability_conditions: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    parent_hypothesis_id: Optional[str] = None
    refinement_reason: Optional[str] = None

    def record_evidence(self, experiment_id: str) -> None:
        if experiment_id not in self.evidence_ids:
            self.evidence_ids.append(experiment_id)
        if self.epistemic_state in (EpistemicState.HYPOTHESIS, EpistemicState.EXPERIMENT):
            self.epistemic_state = EpistemicState.EVIDENCE
        self.updated_at = time.time()

    def record_counterexample(self, counterexample_id: str, explanation: str) -> None:
        if counterexample_id not in self.counterexample_ids:
            self.counterexample_ids.append(counterexample_id)
        self.epistemic_state = EpistemicState.COUNTEREXAMPLE
        self.refinement_reason = explanation
        # Counterexample demotes universality level
        if self.universality_level > UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE:
            self.universality_level = UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE
        self.updated_at = time.time()

    def record_proof(self, proof_id: str, assumed_preconditions: List[str]) -> None:
        if proof_id not in self.proof_ids:
            self.proof_ids.append(proof_id)
        self.epistemic_state = EpistemicState.PROOF
        self.assumptions.extend([a for a in assumed_preconditions if a not in self.assumptions])
        if self.universality_level < UniversalityLevel.LEVEL_6_FORMAL_PROOF_UNDER_ASSUMPTIONS:
            self.universality_level = UniversalityLevel.LEVEL_6_FORMAL_PROOF_UNDER_ASSUMPTIONS
        self.updated_at = time.time()

    def mark_unknown(self, reason: str) -> None:
        self.epistemic_state = EpistemicState.UNKNOWN
        self.refinement_reason = reason
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["epistemic_state"] = self.epistemic_state.value
        data["universality_level"] = int(self.universality_level.value)
        return data
