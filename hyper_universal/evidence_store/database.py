"""
hyper_universal/evidence_store/database.py
Self-Improving Pathway Database:
Maintains a persistent local ledger of discovered and verified pathways,
enabling historical learning without reusing stale or unverified results.
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PathwayRecord:
    workload_id: str
    contract_hash: str = "hash_default"
    contract_version: str = "1.0.0"
    pathway_name: str = "default_pathway"
    candidate_id: str = "cand_0"
    algorithm_family: str = "GENERAL"
    transformation_kinds: List[str] = field(default_factory=list)
    hardware_fingerprint: str = "Intel Core i5 AVX2"
    backend: str = "CPU_AVX2"
    input_shape: List[int] = field(default_factory=list)
    is_verified: bool = True
    verification_status: str = "EXACT_VERIFIED"
    measured_speedup: float = 1.0
    speedup: float = 1.0
    measured_latency_ms: float = 0.0
    peak_memory_mb: float = 0.0
    max_relative_error: float = 0.0
    verified_at_timestamp: float = field(default_factory=time.time)
    confidence_score: float = 1.0
    failure_reason: Optional[str] = None

    def __post_init__(self):
        if self.verification_status == "FAILED_CORRECTNESS":
            self.is_verified = False
        elif self.verification_status in ["EXACT_VERIFIED", "CONTRACT_VERIFIED", "APPROXIMATE_VERIFIED"]:
            self.is_verified = True

        if self.speedup != 1.0 and self.measured_speedup == 1.0:
            self.measured_speedup = self.speedup
        elif self.measured_speedup != 1.0 and self.speedup == 1.0:
            self.speedup = self.measured_speedup

        if self.candidate_id and self.pathway_name == "default_pathway":
            self.pathway_name = self.candidate_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "contract_hash": self.contract_hash,
            "contract_version": self.contract_version,
            "candidate_id": self.candidate_id,
            "pathway_name": self.pathway_name,
            "algorithm_family": self.algorithm_family,
            "backend": self.backend,
            "is_verified": self.is_verified,
            "verification_status": self.verification_status,
            "speedup": round(self.speedup, 2),
            "measured_speedup": round(self.measured_speedup, 2),
            "measured_latency_ms": round(self.measured_latency_ms, 3),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "failure_reason": self.failure_reason,
            "verified_at_timestamp": self.verified_at_timestamp,
        }


class PathwayEvidenceStore:
    """Persistent local evidence database for discovered optimization pathways."""

    def __init__(self, db_path: str = "reports/pathway_evidence_database.json"):
        self.db_path = db_path
        self.records: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = {}
        else:
            self.records = {}

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)

    def record_candidate(self, record: PathwayRecord):
        key = f"{record.workload_id}::{record.candidate_id}"
        self.records[key] = record.to_dict()
        self.save()

    def record_pathway(self, record: PathwayRecord):
        self.record_candidate(record)

    def get_by_workload(self, workload_id: str) -> List[PathwayRecord]:
        results = []
        for r_dict in self.records.values():
            if r_dict.get("workload_id") == workload_id:
                results.append(
                    PathwayRecord(
                        workload_id=r_dict["workload_id"],
                        candidate_id=r_dict.get("candidate_id", ""),
                        pathway_name=r_dict.get("pathway_name", ""),
                        algorithm_family=r_dict.get("algorithm_family", "GENERAL"),
                        backend=r_dict.get("backend", "CPU_AVX2"),
                        verification_status=r_dict.get("verification_status", "UNCERTIFIED"),
                        speedup=r_dict.get("speedup", 1.0),
                        measured_speedup=r_dict.get("measured_speedup", 1.0),
                        measured_latency_ms=r_dict.get("measured_latency_ms", 0.0),
                        peak_memory_mb=r_dict.get("peak_memory_mb", 0.0),
                        failure_reason=r_dict.get("failure_reason"),
                    )
                )
        return results

    def list_all(self) -> List[PathwayRecord]:
        return [
            PathwayRecord(
                workload_id=r["workload_id"],
                candidate_id=r.get("candidate_id", ""),
                pathway_name=r.get("pathway_name", ""),
                algorithm_family=r.get("algorithm_family", "GENERAL"),
                backend=r.get("backend", "CPU_AVX2"),
                verification_status=r.get("verification_status", "UNCERTIFIED"),
                speedup=r.get("speedup", 1.0),
                measured_speedup=r.get("measured_speedup", 1.0),
                measured_latency_ms=r.get("measured_latency_ms", 0.0),
                peak_memory_mb=r.get("peak_memory_mb", 0.0),
                failure_reason=r.get("failure_reason"),
            )
            for r in self.records.values()
        ]

    def summary(self) -> Dict[str, Any]:
        all_recs = list(self.records.values())
        total = len(all_recs)
        exact_cnt = sum(1 for r in all_recs if r.get("verification_status") == "EXACT_VERIFIED")
        contract_cnt = sum(1 for r in all_recs if r.get("verification_status") == "CONTRACT_VERIFIED")
        approx_cnt = sum(1 for r in all_recs if r.get("verification_status") == "APPROXIMATE_VERIFIED")
        failed_cnt = sum(1 for r in all_recs if r.get("verification_status") == "FAILED_CORRECTNESS")

        passed = exact_cnt + contract_cnt + approx_cnt
        parity_pct = (passed / total * 100.0) if total > 0 else 100.0

        return {
            "total_records": total,
            "exact_verified_count": exact_cnt,
            "contract_verified_count": contract_cnt,
            "approximate_verified_count": approx_cnt,
            "failed_correctness_count": failed_cnt,
            "contract_parity_percentage": round(parity_pct, 1),
        }

    def get_best_pathway(self, workload_id: str, contract_hash: str) -> Optional[Dict[str, Any]]:
        matching = [
            r for r in self.records.values()
            if r["workload_id"] == workload_id and r.get("is_verified", False)
        ]
        if not matching:
            return None
        return max(matching, key=lambda x: x.get("measured_speedup", 1.0))

    def invalidate_workload(self, workload_id: str):
        to_del = [k for k in self.records if k.startswith(f"{workload_id}::")]
        for k in to_del:
            del self.records[k]
        self.save()

    def get_all_records(self) -> List[Dict[str, Any]]:
        return list(self.records.values())
