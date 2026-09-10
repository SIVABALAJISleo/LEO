"""
hyper_x/wormhole_compiler/necessity_certificate.py
=============================================================================
Causal Necessity Certificate (Section 7)
=============================================================================
Provides a cryptographically grounded, machine-readable certificate for every
operation analyzed for elimination.

Statuses:
  - NECESSARY_PROVEN: Operation cannot be eliminated without violating the contract.
  - ELIMINATED_VERIFIED: Operation provably eliminated; survived multi-verifier & adversarial battery.
  - CONDITIONAL: Eliminated only under specific input sub-domains or sparsity thresholds.
  - FAILED: Candidate elimination attempted but falsified.
  - UNKNOWN: Inconclusive; causal necessity cannot be proven or disproven.

CRITICAL RULE:
Never represent UNKNOWN as PASS.
"""

from __future__ import annotations
import time
import json
import hashlib
import enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


class NecessityStatus(str, enum.Enum):
    NECESSARY_PROVEN = "NECESSARY_PROVEN"
    ELIMINATED_VERIFIED = "ELIMINATED_VERIFIED"
    CONDITIONAL = "CONDITIONAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass
class CausalNecessityCertificate:
    """
    Formal machine-readable certificate documenting whether an operation is
    strictly necessary or provably eliminated.
    """
    certificate_id: str
    operation_id: str
    workload_id: str
    observable: str
    dependency_path: List[str]
    elimination_attempt: str
    test_inputs_count: int
    counterexamples: List[Dict[str, Any]]
    adversarial_results: Dict[str, Any]
    holdout_results: Dict[str, Any]
    formal_proof_status: str  # "FORMALLY_PROVEN", "EMPIRICALLY_VALIDATED", "FALSIFIED", "UNPROVEN"
    empirical_confidence: float  # 0.0 to 1.0
    fallback_strategy: str
    final_status: NecessityStatus
    provenance: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    software_version: str = "HYPER-Wormhole-v2.0"
    hardware_identity: str = "Intel Core i5-12450H + Intel UHD Graphics"
    sha256_signature: str = ""

    def __post_init__(self):
        if not self.sha256_signature:
            self.sha256_signature = self.compute_signature()

    def compute_signature(self) -> str:
        payload = (
            f"{self.certificate_id}:{self.operation_id}:{self.workload_id}:"
            f"{self.final_status.value}:{self.formal_proof_status}:{self.timestamp}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["final_status"] = self.final_status.value
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @staticmethod
    def create_eliminated_verified(
        operation_id: str,
        workload_id: str,
        observable: str,
        dependency_path: List[str],
        elimination_attempt: str,
        adversarial_results: Dict[str, Any],
        holdout_results: Dict[str, Any],
        fallback_strategy: str,
        provenance: Dict[str, Any],
        empirical_confidence: float = 0.9999,
    ) -> CausalNecessityCertificate:
        cid = f"CERT_ELIM_{operation_id}_{int(time.time()*1000)}"
        return CausalNecessityCertificate(
            certificate_id=cid,
            operation_id=operation_id,
            workload_id=workload_id,
            observable=observable,
            dependency_path=dependency_path,
            elimination_attempt=elimination_attempt,
            test_inputs_count=adversarial_results.get("tests_run", 8),
            counterexamples=[],
            adversarial_results=adversarial_results,
            holdout_results=holdout_results,
            formal_proof_status="EMPIRICALLY_VALIDATED",
            empirical_confidence=empirical_confidence,
            fallback_strategy=fallback_strategy,
            final_status=NecessityStatus.ELIMINATED_VERIFIED,
            provenance=provenance,
        )

    @staticmethod
    def create_necessary_proven(
        operation_id: str,
        workload_id: str,
        observable: str,
        dependency_path: List[str],
        counterexamples: List[Dict[str, Any]],
        proof_status: str,
        provenance: Dict[str, Any],
        explanation: str = "",
    ) -> CausalNecessityCertificate:
        cid = f"CERT_NEC_{operation_id}_{int(time.time()*1000)}"
        return CausalNecessityCertificate(
            certificate_id=cid,
            operation_id=operation_id,
            workload_id=workload_id,
            observable=observable,
            dependency_path=dependency_path,
            elimination_attempt="counterfactual_removal",
            test_inputs_count=len(counterexamples),
            counterexamples=counterexamples,
            adversarial_results={"passed": 0, "failed": len(counterexamples)},
            holdout_results={"passed": False, "reason": "Operation proved indispensable"},
            formal_proof_status=proof_status,
            empirical_confidence=1.0,
            fallback_strategy="exact_native_computation",
            final_status=NecessityStatus.NECESSARY_PROVEN,
            provenance=provenance,
        )
