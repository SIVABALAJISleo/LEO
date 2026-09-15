"""
hyper_x/ahce/evidence.py
========================
Evidence ledger entry and validation models for AHCE.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
import time
from .provenance import EvidenceProvenance, ProvenanceTag


@dataclass
class AHCETelemetryRecord:
    latency_ms: float
    cpu_utilization_pct: float
    ram_used_mb: float
    cache_hits: int = 0
    cache_misses: int = 0
    work_steals: int = 0


@dataclass
class AHCEEvidenceRecord:
    experiment_id: str
    timestamp: float
    workload_id: str
    contract_id: str
    signature_hash: str
    strategy_name: str
    provenance: EvidenceProvenance
    reference_latency_ms: float
    candidate_latency_ms: float
    end_to_end_latency_ms: float
    speedup: float
    reference_necessary_work: float
    candidate_necessary_work: float
    work_reduction_pct: float
    correctness_status: str  # PASS / FAIL
    error_metric: float
    holdout_status: str      # PASS / FAIL / NOT_EVALUATED
    adversarial_status: str  # PASS / FAIL / NOT_EVALUATED
    telemetry: Optional[AHCETelemetryRecord] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["provenance"] = self.provenance.value
        return d
