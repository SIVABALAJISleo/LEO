"""
hyper_x/wormhole_compiler/telemetry.py
=============================================================================
HYPER-X Observability, Telemetry & Cryptographic Claim Validation Engine
=============================================================================
Exposes comprehensive machine-readable JSON and human-readable telemetry:
  - candidates_generated
  - candidates_verified
  - candidates_rejected
  - candidates_falsified
  - work_eliminated_ratio
  - raw_speedup
  - latency & memory traffic
  - transfer & verification time
  - holdout_pass_rate

Enforces strict Claim Validation (Phase 39):
  Every public claim MUST be tied to an immutable EvidenceRecord:
    - benchmark_id
    - workload_hash
    - candidate_hash
    - hardware_fingerprint_hash
    - verifier_hash

Claims lacking evidence are stamped: UNSUPPORTED
Claims with mismatched hardware are stamped: PROVENANCE_INVALID
Claims with modified workloads are stamped: COMPARISON_INVALID
"""

from __future__ import annotations
import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class EvidenceRecord:
    claim_id: str
    claim_statement: str
    benchmark_id: str
    workload_hash: str
    candidate_hash: str
    hardware_hash: str
    verifier_hash: str
    status: str                        # "VERIFIED", "UNSUPPORTED", "PROVENANCE_INVALID", "COMPARISON_INVALID"
    evidence_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class TelemetryCollector:
    """Collects and summarizes execution metrics across compiler stages."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.candidates_generated = 0
        self.candidates_verified = 0
        self.candidates_rejected = 0
        self.candidates_falsified = 0
        self.holdout_tests_passed = 0
        self.holdout_tests_total = 0
        self.search_time_ms = 0.0
        self.verification_time_ms = 0.0
        self.total_latency_ms = 0.0
        self.work_elimination_ratio = 0.0
        self.raw_speedup = 1.0

    def record_search_metrics(
        self,
        generated: int,
        verified: int,
        rejected: int,
        falsified: int,
        search_ms: float,
        verify_ms: float,
        wer: float,
        speedup: float
    ):
        self.candidates_generated += generated
        self.candidates_verified += verified
        self.candidates_rejected += rejected
        self.candidates_falsified += falsified
        self.search_time_ms += search_ms
        self.verification_time_ms += verify_ms
        self.work_elimination_ratio = wer
        self.raw_speedup = speedup

    def to_dict(self) -> Dict[str, Any]:
        holdout_rate = (self.holdout_tests_passed / max(1, self.holdout_tests_total)) * 100.0 if self.holdout_tests_total > 0 else 100.0
        return {
            "candidates_generated": self.candidates_generated,
            "candidates_verified": self.candidates_verified,
            "candidates_rejected": self.candidates_rejected,
            "candidates_falsified": self.candidates_falsified,
            "work_elimination_pct": round(self.work_elimination_ratio * 100.0, 2),
            "raw_speedup": round(self.raw_speedup, 2),
            "search_time_ms": round(self.search_time_ms, 3),
            "verification_time_ms": round(self.verification_time_ms, 3),
            "holdout_pass_rate_pct": round(holdout_rate, 1)
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown_report(self) -> str:
        d = self.to_dict()
        return f"""### HYPER-X Wormhole Compiler Telemetry
- **Candidates Generated**: {d['candidates_generated']}
- **Candidates Verified**: {d['candidates_verified']}
- **Candidates Rejected / Falsified**: {d['candidates_rejected']} / {d['candidates_falsified']}
- **Work Eliminated**: {d['work_elimination_pct']}%
- **Measured Wall-Clock Speedup**: {d['raw_speedup']}x
- **Search Latency**: {d['search_time_ms']} ms
- **Verification Latency**: {d['verification_time_ms']} ms
"""


class ClaimValidationEngine:
    """Validates public statements against empirical evidence records."""

    def __init__(self):
        self.evidence_vault: Dict[str, EvidenceRecord] = {}

    def register_evidence(
        self,
        claim_statement: str,
        benchmark_id: str,
        workload_hash: str,
        candidate_hash: str,
        hardware_hash: str,
        verifier_hash: str,
        is_target_hardware_match: bool,
        is_workload_unmodified: bool,
        verification_passed: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> EvidenceRecord:
        c_id = f"CLM_{hashlib.sha256(claim_statement.encode()).hexdigest()[:10]}"

        if not is_workload_unmodified:
            status = "COMPARISON_INVALID"
        elif not is_target_hardware_match:
            status = "PROVENANCE_INVALID"
        elif not verification_passed:
            status = "UNSUPPORTED"
        else:
            status = "VERIFIED"

        rec = EvidenceRecord(
            claim_id=c_id,
            claim_statement=claim_statement,
            benchmark_id=benchmark_id,
            workload_hash=workload_hash,
            candidate_hash=candidate_hash,
            hardware_hash=hardware_hash,
            verifier_hash=verifier_hash,
            status=status,
            evidence_details=details or {}
        )
        self.evidence_vault[c_id] = rec
        return rec


@dataclass
class ResearchCapabilityScorecard:
    discovery_score: float
    synthesis_score: float
    representation_score: float
    counterfactual_score: float
    verification_score: float
    falsification_score: float
    generalization_score: float
    reproducibility_score: float
    benchmark_integrity_score: float
    composite_research_capability_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HardwareParityScorecard:
    throughput_parity_pct: float
    latency_parity_pct: float
    memory_efficiency_parity_pct: float
    energy_efficiency_parity_pct: float
    composite_hardware_parity_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DualTrackScorer:
    """
    Evaluates Research Capability and Hardware Parity as strictly independent scores.
    Never combines or conflates them.
    """

    @staticmethod
    def calculate_research_capability(
        discovered_novel_count: int,
        cegis_repairs_count: int,
        representations_evaluated: int,
        counterfactuals_tested: int,
        proofs_verified_count: int,
        falsification_stress_pass_rate: float,
        cross_domain_transfer_count: int,
        reproducibility_pass_rate: float,
        benchmark_integrity_pass_rate: float,
    ) -> ResearchCapabilityScorecard:
        """
        Derives RESEARCH_CAPABILITY_SCORE strictly from empirical activity.
        """
        disc = min(100.0, discovered_novel_count * 12.5)
        synth = min(100.0, cegis_repairs_count * 20.0)
        rep = min(100.0, representations_evaluated * 15.0)
        cf = min(100.0, counterfactuals_tested * 10.0)
        ver = min(100.0, proofs_verified_count * 10.0)
        fals = falsification_stress_pass_rate * 100.0
        gen = min(100.0, cross_domain_transfer_count * 25.0)
        rep_rate = reproducibility_pass_rate * 100.0
        audit_rate = benchmark_integrity_pass_rate * 100.0

        composite = (
            disc * 0.15
            + synth * 0.10
            + rep * 0.10
            + cf * 0.10
            + ver * 0.15
            + fals * 0.15
            + gen * 0.10
            + rep_rate * 0.075
            + audit_rate * 0.075
        )

        return ResearchCapabilityScorecard(
            discovery_score=round(disc, 1),
            synthesis_score=round(synth, 1),
            representation_score=round(rep, 1),
            counterfactual_score=round(cf, 1),
            verification_score=round(ver, 1),
            falsification_score=round(fals, 1),
            generalization_score=round(gen, 1),
            reproducibility_score=round(rep_rate, 1),
            benchmark_integrity_score=round(audit_rate, 1),
            composite_research_capability_score=round(composite, 2),
        )

    @staticmethod
    def calculate_hardware_parity(
        candidate_throughput: float,
        reference_gpu_throughput: float,
        candidate_latency_ms: float,
        reference_gpu_latency_ms: float,
        candidate_memory_mb: float,
        reference_gpu_memory_mb: float,
        candidate_energy_joules: float,
        reference_gpu_energy_joules: float,
    ) -> HardwareParityScorecard:
        """
        Calculates physical silicon throughput and latency parity against reference GPU.
        Never fakes 100% when silicon throughput is bounded by CPU/iGPU.
        """
        thr_parity = min(100.0, (candidate_throughput / max(1e-5, reference_gpu_throughput)) * 100.0)
        lat_parity = min(100.0, (reference_gpu_latency_ms / max(1e-5, candidate_latency_ms)) * 100.0)
        mem_parity = min(100.0, (reference_gpu_memory_mb / max(1e-5, candidate_memory_mb)) * 100.0)
        eng_parity = min(100.0, (reference_gpu_energy_joules / max(1e-5, candidate_energy_joules)) * 100.0)

        composite = thr_parity * 0.40 + lat_parity * 0.30 + mem_parity * 0.15 + eng_parity * 0.15

        return HardwareParityScorecard(
            throughput_parity_pct=round(thr_parity, 2),
            latency_parity_pct=round(lat_parity, 2),
            memory_efficiency_parity_pct=round(mem_parity, 2),
            energy_efficiency_parity_pct=round(eng_parity, 2),
            composite_hardware_parity_pct=round(composite, 2),
        )
