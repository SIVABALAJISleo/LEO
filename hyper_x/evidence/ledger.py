#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/evidence/ledger.py
==========================
Phase 8: Authoritative Evidence Ledger & Candidate Registry.
Maintains persistent evidence with full provenance tracking.
"""

from __future__ import annotations
import os
import json
import time
from typing import Dict, Any, List, Optional
from hyper_x.certificates.certificate import ExecutionCertificate


class EvidenceLedger:
    """Stores all verified execution records, benchmarks, and candidate pathways."""

    def __init__(
        self,
        ledger_path: str = "evidence_ledger.json",
        registry_path: str = "candidate_registry.json"
    ):
        self.ledger_path = ledger_path
        self.registry_path = registry_path
        self.entries: List[Dict[str, Any]] = self._load_ledger()
        self.candidates: Dict[str, Any] = self._load_registry()

    def _load_ledger(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _load_registry(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return list(data.values())
            except Exception:
                return []
        return []

    def record_certificate(self, cert: ExecutionCertificate):
        entry = cert.to_dict()
        self.entries.append(entry)
        self._save_ledger()

        # Update candidate registry list
        cid = cert.candidate_hash
        candidate_entry = {
            "candidate_id": cid,
            "workload_id": cert.workload_id,
            "exactness_class": cert.exactness_class,
            "correctness_result": cert.correctness_result,
            "work_elimination_pct": round(cert.work_eliminated_ratio * 100.0, 2),
            "throughput_ops_per_sec": cert.throughput_ops_per_sec,
            "provenance": cert.provenance,
            "hardware": cert.hardware_fingerprint,
            "last_verified_timestamp": cert.timestamp
        }
        # Replace or append
        existing_idx = next((i for i, c in enumerate(self.candidates) if c.get("candidate_id") == cid), None)
        if existing_idx is not None:
            self.candidates[existing_idx] = candidate_entry
        else:
            self.candidates.append(candidate_entry)
        self._save_registry()

    def _save_ledger(self):
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)

    def _save_registry(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.candidates, f, indent=2)

    def get_verified_records(self) -> List[Dict[str, Any]]:
        return [e for e in self.entries if e.get("correctness_result") == "PASS"]
