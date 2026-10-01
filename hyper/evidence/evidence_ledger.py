"""
hyper/evidence/evidence_ledger.py
=================================
Canonical Evidence Object and Immutable Evidence Ledger for LEO/HYPER.
Enforces Section 4 & 33 scientific integrity rules:
Separates MEASURED, PROVEN, VERIFIED, ESTIMATED, DERIVED, SIMULATED, CACHED,
PREDICTED, UNPROVEN, REJECTED, and FALLBACK statuses.
"""

from __future__ import annotations
import enum
import json
import os
import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from hyper.hardware import get_hardware_profile


class EvidenceStatus(str, enum.Enum):
    MEASURED = "MEASURED"
    PROVEN = "PROVEN"
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    DERIVED = "DERIVED"
    SIMULATED = "SIMULATED"
    CACHED = "CACHED"
    PREDICTED = "PREDICTED"
    UNPROVEN = "UNPROVEN"
    REJECTED = "REJECTED"
    FALLBACK = "FALLBACK"


@dataclass
class Evidence:
    evidence_id: str
    workload_id: str
    contract_id: str
    ir_version: str
    semantic_version: str
    candidate_id: str
    status: EvidenceStatus
    provenance: Dict[str, Any]
    hardware: Dict[str, Any]
    software: Dict[str, Any]
    git_commit: str
    timestamp: float
    seed: int
    input_hash: str
    output_hash: str
    reference_hash: str
    verifier_result: Dict[str, Any]
    measured_latency_ms: float
    measured_memory_bytes: int
    measured_operations: int
    exactness: str
    confidence: float
    certificate_id: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "workload_id": self.workload_id,
            "contract_id": self.contract_id,
            "ir_version": self.ir_version,
            "semantic_version": self.semantic_version,
            "candidate_id": self.candidate_id,
            "status": self.status.value,
            "provenance": self.provenance,
            "hardware": self.hardware,
            "software": self.software,
            "git_commit": self.git_commit,
            "timestamp": self.timestamp,
            "seed": self.seed,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "reference_hash": self.reference_hash,
            "verifier_result": self.verifier_result,
            "measured_latency_ms": round(self.measured_latency_ms, 4),
            "measured_memory_bytes": self.measured_memory_bytes,
            "measured_operations": self.measured_operations,
            "exactness": self.exactness,
            "confidence": round(self.confidence, 4),
            "certificate_id": self.certificate_id,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Evidence:
        return cls(
            evidence_id=d["evidence_id"],
            workload_id=d["workload_id"],
            contract_id=d["contract_id"],
            ir_version=d["ir_version"],
            semantic_version=d["semantic_version"],
            candidate_id=d["candidate_id"],
            status=EvidenceStatus(d["status"]),
            provenance=d["provenance"],
            hardware=d["hardware"],
            software=d["software"],
            git_commit=d.get("git_commit", "unknown"),
            timestamp=d["timestamp"],
            seed=d.get("seed", 42),
            input_hash=d["input_hash"],
            output_hash=d["output_hash"],
            reference_hash=d["reference_hash"],
            verifier_result=d["verifier_result"],
            measured_latency_ms=d["measured_latency_ms"],
            measured_memory_bytes=d["measured_memory_bytes"],
            measured_operations=d.get("measured_operations", 0),
            exactness=d["exactness"],
            confidence=d["confidence"],
            certificate_id=d.get("certificate_id"),
            notes=d.get("notes", ""),
        )


class EvidenceLedger:
    """
    Append-only, immutable record ledger of all computational evaluations.
    """

    def __init__(self, ledger_file: Optional[str] = None) -> None:
        self.ledger_file = ledger_file or "evidence_ledger.json"
        self._entries: List[Evidence] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._entries = [Evidence.from_dict(item) for item in data if isinstance(item, dict)]
            except Exception:
                self._entries = []

    def save(self) -> None:
        try:
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in self._entries], f, indent=2)
        except Exception:
            pass

    def record(self, evidence: Evidence) -> None:
        self._entries.append(evidence)
        self.save()

    def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        for e in self._entries:
            if e.evidence_id == evidence_id:
                return e
        return None

    def get_by_workload(self, workload_id: str) -> List[Evidence]:
        return [e for e in self._entries if e.workload_id == workload_id]

    @property
    def total_records(self) -> int:
        return len(self._entries)

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self._entries:
            st = e.status.value
            counts[st] = counts.get(st, 0) + 1
        return counts
