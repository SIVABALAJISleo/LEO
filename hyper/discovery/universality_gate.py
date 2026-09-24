"""
hyper/discovery/universality_gate.py
===================================
Rigorous Universality Gate & 16-State Discovery Result Machine.

Implements Sections 31 & 34 of the Master Architecture:
- 16-State Result Machine:
    DISCOVERED, VERIFIED, GENERALIZED, PROVEN, TARGET_REACHED,
    IMPROVEMENT_FOUND, COUNTEREXAMPLE_FOUND, SEARCH_SATURATED,
    BARRIER, UNKNOWN, FAILURE, INVALID_COMPARISON, UNVERIFIED,
    SIMULATED, REFERENCE_ONLY, GUARANTEED.
- Universality Gate with 12 Mandatory Pre-flight Verification Checkpoints:
    [1]  domain formally defined
    [2]  contract formally defined
    [3]  correctness established
    [4]  independent verification passed
    [5]  counterexample search conducted
    [6]  generalization demonstrated across >=100 diverse cases
    [7]  reproducibility guaranteed (fixed seed, deterministic env)
    [8]  performance measured on physical hardware (never simulated)
    [9]  resource evidence within host limits (RAM, Bandwidth, TDP)
    [10] no hidden computation / zero-leakage verified
    [11] no unfair caching / cold-cache protocol verified
    [12] formal proof or verified evidence gate passed
- Hard Rule: Only when ALL 12 checkpoints pass can the status transition to GUARANTEED.
  Otherwise, it remains strictly NOT_PROVEN or the appropriate intermediate state.
"""

from __future__ import annotations
import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class DiscoveryResultState(Enum):
    DISCOVERED = "DISCOVERED"
    VERIFIED = "VERIFIED"
    GENERALIZED = "GENERALIZED"
    PROVEN = "PROVEN"
    TARGET_REACHED = "TARGET_REACHED"
    IMPROVEMENT_FOUND = "IMPROVEMENT_FOUND"
    COUNTEREXAMPLE_FOUND = "COUNTEREXAMPLE_FOUND"
    SEARCH_SATURATED = "SEARCH_SATURATED"
    BARRIER = "BARRIER"
    UNKNOWN = "UNKNOWN"
    FAILURE = "FAILURE"
    INVALID_COMPARISON = "INVALID_COMPARISON"
    UNVERIFIED = "UNVERIFIED"
    SIMULATED = "SIMULATED"
    REFERENCE_ONLY = "REFERENCE_ONLY"
    GUARANTEED = "GUARANTEED"


class UniversalityGateChecklist(BaseModel):
    # 12 Mandatory Gates
    domain_formally_defined: bool = False
    contract_formally_defined: bool = False
    correctness_established: bool = False
    independent_verification_passed: bool = False
    counterexample_search_conducted: bool = False
    generalization_demonstrated: bool = False
    reproducibility_guaranteed: bool = False
    performance_evidence_measured: bool = False
    resource_evidence_verified: bool = False
    no_hidden_computation_verified: bool = False
    no_unfair_caching_verified: bool = False
    proof_or_formal_evidence_passed: bool = False

    # Auditing notes for each gate
    audit_notes: Dict[str, str] = Field(default_factory=dict)

    def passed_count(self) -> int:
        fields = [
            self.domain_formally_defined,
            self.contract_formally_defined,
            self.correctness_established,
            self.independent_verification_passed,
            self.counterexample_search_conducted,
            self.generalization_demonstrated,
            self.reproducibility_guaranteed,
            self.performance_evidence_measured,
            self.resource_evidence_verified,
            self.no_hidden_computation_verified,
            self.no_unfair_caching_verified,
            self.proof_or_formal_evidence_passed,
        ]
        return sum(1 for f in fields if f)

    def total_count(self) -> int:
        return 12

    def is_all_passed(self) -> bool:
        return self.passed_count() == self.total_count()

    def get_unpassed_gates(self) -> List[str]:
        mapping = {
            "domain_formally_defined": self.domain_formally_defined,
            "contract_formally_defined": self.contract_formally_defined,
            "correctness_established": self.correctness_established,
            "independent_verification_passed": self.independent_verification_passed,
            "counterexample_search_conducted": self.counterexample_search_conducted,
            "generalization_demonstrated": self.generalization_demonstrated,
            "reproducibility_guaranteed": self.reproducibility_guaranteed,
            "performance_evidence_measured": self.performance_evidence_measured,
            "resource_evidence_verified": self.resource_evidence_verified,
            "no_hidden_computation_verified": self.no_hidden_computation_verified,
            "no_unfair_caching_verified": self.no_unfair_caching_verified,
            "proof_or_formal_evidence_passed": self.proof_or_formal_evidence_passed,
        }
        return [k for k, v in mapping.items() if not v]


class UniversalityAuditReport(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"ugate-{uuid.uuid4().hex[:8]}")
    workload_id: str
    pathway_name: str
    initial_state: DiscoveryResultState
    final_state: DiscoveryResultState
    checklist: UniversalityGateChecklist
    passed_percentage: float
    verdict: str  # "GUARANTEED" or "NOT_PROVEN"
    rejection_reasons: List[str] = Field(default_factory=list)
    audit_timestamp: float = Field(default_factory=time.time)
    audit_hash: str = ""

    def compute_hash(self) -> str:
        content = f"{self.workload_id}:{self.pathway_name}:{self.verdict}:{self.passed_percentage}"
        self.audit_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.audit_hash


class UniversalityGate:
    """
    Constitutional Gatekeeper for universal pathway claims.
    Enforces evidence-based state transitions and forbids premature 'GUARANTEED' declarations.
    """

    ALLOWED_TRANSITIONS: Dict[DiscoveryResultState, Set[DiscoveryResultState]] = {
        DiscoveryResultState.UNKNOWN: {
            DiscoveryResultState.DISCOVERED,
            DiscoveryResultState.UNVERIFIED,
            DiscoveryResultState.FAILURE,
        },
        DiscoveryResultState.DISCOVERED: {
            DiscoveryResultState.VERIFIED,
            DiscoveryResultState.IMPROVEMENT_FOUND,
            DiscoveryResultState.COUNTEREXAMPLE_FOUND,
            DiscoveryResultState.FAILURE,
            DiscoveryResultState.SIMULATED,
        },
        DiscoveryResultState.SIMULATED: {
            DiscoveryResultState.REFERENCE_ONLY,
            DiscoveryResultState.UNVERIFIED,
            DiscoveryResultState.DISCOVERED,
        },
        DiscoveryResultState.REFERENCE_ONLY: {
            DiscoveryResultState.INVALID_COMPARISON,
            DiscoveryResultState.DISCOVERED,
        },
        DiscoveryResultState.VERIFIED: {
            DiscoveryResultState.GENERALIZED,
            DiscoveryResultState.TARGET_REACHED,
            DiscoveryResultState.COUNTEREXAMPLE_FOUND,
            DiscoveryResultState.SEARCH_SATURATED,
        },
        DiscoveryResultState.GENERALIZED: {
            DiscoveryResultState.PROVEN,
            DiscoveryResultState.COUNTEREXAMPLE_FOUND,
            DiscoveryResultState.SEARCH_SATURATED,
        },
        DiscoveryResultState.PROVEN: {
            DiscoveryResultState.GUARANTEED,
            DiscoveryResultState.COUNTEREXAMPLE_FOUND,
        },
        DiscoveryResultState.TARGET_REACHED: {
            DiscoveryResultState.GENERALIZED,
            DiscoveryResultState.PROVEN,
            DiscoveryResultState.GUARANTEED,
        },
        DiscoveryResultState.COUNTEREXAMPLE_FOUND: {
            DiscoveryResultState.BARRIER,
            DiscoveryResultState.UNKNOWN,
            DiscoveryResultState.DISCOVERED,
        },
        DiscoveryResultState.SEARCH_SATURATED: {
            DiscoveryResultState.BARRIER,
            DiscoveryResultState.UNKNOWN,
        },
        DiscoveryResultState.BARRIER: {
            DiscoveryResultState.UNKNOWN,
        },
        DiscoveryResultState.FAILURE: {
            DiscoveryResultState.UNKNOWN,
        },
        DiscoveryResultState.INVALID_COMPARISON: {
            DiscoveryResultState.UNKNOWN,
        },
        DiscoveryResultState.UNVERIFIED: {
            DiscoveryResultState.VERIFIED,
            DiscoveryResultState.FAILURE,
        },
        DiscoveryResultState.IMPROVEMENT_FOUND: {
            DiscoveryResultState.TARGET_REACHED,
            DiscoveryResultState.VERIFIED,
        },
        DiscoveryResultState.GUARANTEED: set(),  # Terminal state
    }

    def __init__(self) -> None:
        self.audit_log: List[UniversalityAuditReport] = []

    def can_transition(
        self,
        current_state: DiscoveryResultState,
        target_state: DiscoveryResultState,
    ) -> bool:
        """Checks if a transition between states is structurally allowed in the DAG."""
        return target_state in self.ALLOWED_TRANSITIONS.get(current_state, set())

    def audit_for_guarantee(
        self,
        workload_id: str,
        pathway_name: str,
        current_state: DiscoveryResultState,
        checklist: UniversalityGateChecklist,
    ) -> UniversalityAuditReport:
        """
        Executes the formal 12-item universality audit.
        Only transitions to GUARANTEED if all 12 items pass.
        Otherwise preserves state and marks verdict as NOT_PROVEN.
        """
        passed = checklist.passed_count()
        total = checklist.total_count()
        pct = round((passed / total) * 100.0, 1)

        unpassed = checklist.get_unpassed_gates()
        rejections = []

        if checklist.is_all_passed():
            if current_state in (DiscoveryResultState.PROVEN, DiscoveryResultState.TARGET_REACHED):
                final_state = DiscoveryResultState.GUARANTEED
                verdict = "GUARANTEED"
            else:
                final_state = current_state
                verdict = "NOT_PROVEN"
                rejections.append(
                    f"Current state ({current_state.value}) must be PROVEN or TARGET_REACHED to reach GUARANTEED."
                )
        else:
            final_state = current_state
            verdict = "NOT_PROVEN"
            for gate in unpassed:
                rejections.append(f"Gate violation: [{gate}] not satisfied.")

        report = UniversalityAuditReport(
            workload_id=workload_id,
            pathway_name=pathway_name,
            initial_state=current_state,
            final_state=final_state,
            checklist=checklist,
            passed_percentage=pct,
            verdict=verdict,
            rejection_reasons=rejections,
        )
        report.compute_hash()
        self.audit_log.append(report)
        return report
