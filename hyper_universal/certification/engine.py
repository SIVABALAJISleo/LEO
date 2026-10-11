"""
hyper_universal/certification/engine.py
Exactness, Correctness and Formal Certification Engine:
Enforces fail-closed multi-tier verification before awarding certification states.
Never trusts candidate-supplied passed flags or self-attestation.
"""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_universal.contracts.contract_engine import UniversalContract, ExactnessRequirement


class CertificationState(str, Enum):
    EXACT_VERIFIED = "EXACT_VERIFIED"
    CONTRACT_VERIFIED = "CONTRACT_VERIFIED"
    APPROXIMATE_VERIFIED = "APPROXIMATE_VERIFIED"
    PROBABILISTICALLY_VERIFIED = "PROBABILISTICALLY_VERIFIED"
    PERFORMANCE_VERIFIED = "PERFORMANCE_VERIFIED"
    FAILED_CORRECTNESS = "FAILED_CORRECTNESS"
    FAILED_PERFORMANCE = "FAILED_PERFORMANCE"
    UNSUPPORTED = "UNSUPPORTED"
    UNCERTIFIED = "UNCERTIFIED"


@dataclass
class FormalCertificate:
    certificate_id: str
    workload_id: str
    contract_hash: str
    state: CertificationState
    is_certified: bool
    max_relative_error: float
    max_absolute_error: float
    reference_latency_ms: float
    candidate_latency_ms: float
    measured_speedup: float
    sample_count: int
    hardware_target: str
    reason: str
    provenance_hash: str = ""

    # Aliases
    @property
    def certification_state(self) -> CertificationState:
        return self.state

    @property
    def speedup(self) -> float:
        return self.measured_speedup

    @property
    def passes_contract(self) -> bool:
        return self.is_certified

    @property
    def evidence_notes(self) -> str:
        return self.reason

    def __post_init__(self):
        payload = f"{self.certificate_id}:{self.workload_id}:{self.state.value}:{self.is_certified}:{self.measured_speedup}"
        object.__setattr__(self, "provenance_hash", hashlib.sha256(payload.encode()).hexdigest())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "workload_id": self.workload_id,
            "contract_hash": self.contract_hash,
            "state": self.state.value,
            "is_certified": self.is_certified,
            "max_relative_error": round(self.max_relative_error, 6),
            "max_absolute_error": round(self.max_absolute_error, 6),
            "reference_latency_ms": round(self.reference_latency_ms, 3),
            "candidate_latency_ms": round(self.candidate_latency_ms, 3),
            "measured_speedup": round(self.measured_speedup, 2),
            "sample_count": self.sample_count,
            "hardware_target": self.hardware_target,
            "reason": self.reason,
            "provenance_hash": self.provenance_hash,
        }


class FormalCertificationEngine:
    """Master certification authority validating candidate execution against independent references."""

    @staticmethod
    def certify(
        contract: UniversalContract,
        reference_output: Any,
        candidate_output: Any,
        ref_latency_ms: float,
        cand_latency_ms: float,
        hardware_target: str = "Intel Core i5 AVX2",
        sample_count: int = 5,
    ) -> FormalCertificate:
        cert_id = f"cert_{contract.workload_id}_{int(time.time() * 1000)}"

        # 1. Correctness validation
        is_valid, rel_err, abs_err, reason = contract.validate_candidate_output(
            reference_output, candidate_output
        )

        speedup = (ref_latency_ms / max(cand_latency_ms, 1e-6)) if cand_latency_ms > 0 else 1.0

        if not is_valid:
            return FormalCertificate(
                certificate_id=cert_id,
                workload_id=contract.workload_id,
                contract_hash=contract.contract_hash,
                state=CertificationState.FAILED_CORRECTNESS,
                is_certified=False,
                max_relative_error=rel_err,
                max_absolute_error=abs_err,
                reference_latency_ms=ref_latency_ms,
                candidate_latency_ms=cand_latency_ms,
                measured_speedup=speedup,
                sample_count=sample_count,
                hardware_target=hardware_target,
                reason=f"Correctness validation failed: {reason}",
            )

        # 2. Performance regression check
        if speedup < 0.8:
            return FormalCertificate(
                certificate_id=cert_id,
                workload_id=contract.workload_id,
                contract_hash=contract.contract_hash,
                state=CertificationState.FAILED_PERFORMANCE,
                is_certified=False,
                max_relative_error=rel_err,
                max_absolute_error=abs_err,
                reference_latency_ms=ref_latency_ms,
                candidate_latency_ms=cand_latency_ms,
                measured_speedup=speedup,
                sample_count=sample_count,
                hardware_target=hardware_target,
                reason=f"Performance regressed: speedup was {speedup:.2f}x (below 0.8x threshold)",
            )

        # 3. Determine verified certification state
        if contract.exactness == ExactnessRequirement.BITWISE_EXACT:
            state = CertificationState.EXACT_VERIFIED
        elif contract.exactness == ExactnessRequirement.NUMERICALLY_EQUIVALENT:
            state = CertificationState.CONTRACT_VERIFIED
        elif contract.exactness in [ExactnessRequirement.APPROXIMATE_BOUNDED, ExactnessRequirement.APPROXIMATE_WITH_TOLERANCE]:
            state = CertificationState.APPROXIMATE_VERIFIED
        elif contract.exactness == ExactnessRequirement.PROBABILISTIC_BOUNDED:
            state = CertificationState.PROBABILISTICALLY_VERIFIED
        else:
            state = CertificationState.PERFORMANCE_VERIFIED

        return FormalCertificate(
            certificate_id=cert_id,
            workload_id=contract.workload_id,
            contract_hash=contract.contract_hash,
            state=state,
            is_certified=True,
            max_relative_error=rel_err,
            max_absolute_error=abs_err,
            reference_latency_ms=ref_latency_ms,
            candidate_latency_ms=cand_latency_ms,
            measured_speedup=speedup,
            sample_count=sample_count,
            hardware_target=hardware_target,
            reason="All contract gates verified and passed",
        )

    def certify_candidate(
        self,
        candidate_id: str,
        contract: UniversalContract,
        candidate_output: Any,
        reference_output: Any,
        candidate_latency_ms: float,
        reference_latency_ms: float,
        backend_name: str = "CPU_AVX2",
        sample_count: int = 5,
    ) -> FormalCertificate:
        cert_id = f"cert_{candidate_id}_{int(time.time() * 1000)}"

        # 1. Correctness validation
        is_valid, rel_err, abs_err, reason = contract.validate_candidate_output(
            reference_output, candidate_output
        )

        speedup = (reference_latency_ms / max(candidate_latency_ms, 1e-6)) if candidate_latency_ms > 0 else (reference_latency_ms if reference_latency_ms > 0 else 1.0)

        if not is_valid:
            return FormalCertificate(
                certificate_id=cert_id,
                workload_id=contract.workload_id,
                contract_hash=contract.contract_hash,
                state=CertificationState.FAILED_CORRECTNESS,
                is_certified=False,
                max_relative_error=rel_err,
                max_absolute_error=abs_err,
                reference_latency_ms=reference_latency_ms,
                candidate_latency_ms=candidate_latency_ms,
                measured_speedup=speedup,
                sample_count=sample_count,
                hardware_target=backend_name,
                reason=f"Correctness validation failed: {reason}",
            )

        # Correctness passed: Determine certification state
        if contract.exactness == ExactnessRequirement.BITWISE_EXACT:
            state = CertificationState.EXACT_VERIFIED
        elif contract.exactness == ExactnessRequirement.NUMERICALLY_EQUIVALENT:
            state = CertificationState.CONTRACT_VERIFIED
        elif contract.exactness in [ExactnessRequirement.APPROXIMATE_BOUNDED, ExactnessRequirement.APPROXIMATE_WITH_TOLERANCE]:
            state = CertificationState.APPROXIMATE_VERIFIED
        elif contract.exactness == ExactnessRequirement.PROBABILISTIC_BOUNDED:
            state = CertificationState.PROBABILISTICALLY_VERIFIED
        else:
            state = CertificationState.PERFORMANCE_VERIFIED

        return FormalCertificate(
            certificate_id=cert_id,
            workload_id=contract.workload_id,
            contract_hash=contract.contract_hash,
            state=state,
            is_certified=True,
            max_relative_error=rel_err,
            max_absolute_error=abs_err,
            reference_latency_ms=reference_latency_ms,
            candidate_latency_ms=candidate_latency_ms,
            measured_speedup=speedup,
            sample_count=sample_count,
            hardware_target=backend_name,
            reason="Contract requirements verified",
        )
