"""
hyper_x/verification/certification_engine.py
============================================
Phase 1, Phase 36, Phase 37: Master Fail-Closed Certification Engine.
Coordinates all 13 modular verification engines and enforces:
- RTXEquivalentGate: Hard multi-constraint gate (Correctness + Contract + Real-Time + Independent + Adversarial + Holdout + Provenance + Resource)
- Universal100Gate: 100% requires ALL declared gates to pass; never a weighted average.
Default: passed = False.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from hyper_x.contract import WorkloadContract
from hyper_x.verification.contract_verifier import ContractVerifier, ContractVerificationResult
from hyper_x.verification.exact_verifier import ExactVerifier, ExactVerificationResult
from hyper_x.verification.numerical_verifier import NumericalVerifier, NumericalVerificationResult
from hyper_x.verification.output_hash_verifier import OutputHashVerifier, OutputHashVerificationResult
from hyper_x.verification.operation_trace_verifier import OperationTraceVerifier, OperationTraceResult
from hyper_x.verification.provenance_verifier import ProvenanceVerifier, ProvenanceVerificationResult
from hyper_x.verification.benchmark_integrity import BenchmarkIntegrityVerifier, BenchmarkIntegrityResult
from hyper_x.verification.cache_integrity import CacheIntegrityVerifier, CacheIntegrityResult
from hyper_x.verification.independent_verifier import IndependentVerifier, IndependentVerificationResult
from hyper_x.verification.adversarial_verifier import AdversarialVerifier, AdversarialVerificationResult
from hyper_x.verification.holdout_verifier import HoldoutVerifier, HoldoutVerificationResult
from hyper_x.verification.realtime_verifier import RealtimeVerifier, RealtimeVerificationResult
from hyper_x.verification.resource_verifier import ResourceVerifier, ResourceVerificationResult


@dataclass
class CertificationReport:
    workload_id: str
    is_certified: bool = False  # Fail-closed default
    rtx_equivalent_gate: bool = False
    universal_100_gate: bool = False
    certification_status: str = "UNKNOWN"  # VERIFIED, FAILED, UNKNOWN, INVALID
    failed_gates: List[str] = field(default_factory=list)
    certificate_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def seal(self) -> str:
        d_str = json.dumps(asdict(self), sort_keys=True)
        self.certificate_hash = hashlib.sha256(d_str.encode("utf-8")).hexdigest()
        return self.certificate_hash

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class CertificationEngine:
    """
    Master certification orchestrator. Fails closed if any verification gate fails or is missing.
    """

    @classmethod
    def certify(
        cls,
        contract: WorkloadContract,
        contract_res: ContractVerificationResult,
        numerical_or_exact_res: Any,
        output_hash_res: OutputHashVerificationResult,
        trace_res: OperationTraceResult,
        provenance_res: ProvenanceVerificationResult,
        integrity_res: BenchmarkIntegrityResult,
        cache_res: CacheIntegrityResult,
        independent_res: IndependentVerificationResult,
        adversarial_res: AdversarialVerificationResult,
        holdout_res: HoldoutVerificationResult,
        realtime_res: RealtimeVerificationResult,
        resource_res: ResourceVerificationResult,
    ) -> CertificationReport:
        failed_gates = []

        if not contract_res.passed:
            failed_gates.append("CONTRACT_GATE")
        if not numerical_or_exact_res.passed:
            failed_gates.append("NUMERICAL_OR_EXACT_GATE")
        if not output_hash_res.passed:
            failed_gates.append("OUTPUT_HASH_GATE")
        if not trace_res.passed:
            failed_gates.append("OPERATION_TRACE_GATE")
        if not provenance_res.passed:
            failed_gates.append("PROVENANCE_GATE")
        if not integrity_res.passed:
            failed_gates.append("BENCHMARK_INTEGRITY_GATE")
        if not cache_res.passed:
            failed_gates.append("CACHE_INTEGRITY_GATE")
        if not independent_res.passed:
            failed_gates.append("INDEPENDENT_VERIFICATION_GATE")
        if not adversarial_res.passed:
            failed_gates.append("ADVERSARIAL_GATE")
        if not holdout_res.passed:
            failed_gates.append("HOLDOUT_GATE")
        if not realtime_res.passed:
            failed_gates.append("REALTIME_GATE")
        if not resource_res.passed:
            failed_gates.append("RESOURCE_GATE")

        # RTX Equivalent Gate & Universal 100 Gate require 100% of declared mandatory gates to pass
        all_passed = (len(failed_gates) == 0)

        status = "VERIFIED" if all_passed else ("INVALID" if not integrity_res.passed else "FAILED")

        report = CertificationReport(
            workload_id=contract.workload_id,
            is_certified=all_passed,
            rtx_equivalent_gate=all_passed,
            universal_100_gate=all_passed,
            certification_status=status,
            failed_gates=failed_gates,
        )
        report.seal()
        return report
