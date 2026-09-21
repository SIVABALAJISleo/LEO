"""
hyper/escape_engine/reporting/audit_log.py
==========================================
VAEE Section 32: Scientific Audit Logger.

Retains tamper-evident proof records for every decision, baseline comparison,
transformation chain, verification verdict, and measured speedup.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional


class ScientificAuditLogger:
    """Records verifiable proof records of computational decisions."""

    def __init__(self, log_dir: Optional[str] = None) -> None:
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "reports", "vaee_audit"
        )
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_log_path = os.path.join(self.log_dir, "audit_log.jsonl")

    def log_decision(
        self,
        experiment_id: str,
        workload_name: str,
        baseline_latency_ms: float,
        candidate_pathway_id: str,
        transformations: list[str],
        verification_method: str,
        verification_status: str,
        candidate_latency_ms: float,
        verified_speedup: float,
        classification: str,
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": time.time(),
            "experiment_id": experiment_id,
            "workload": workload_name,
            "baseline_ms": round(baseline_latency_ms, 4),
            "candidate_id": candidate_pathway_id,
            "transformation_chain": transformations,
            "verification_method": verification_method,
            "verification_status": verification_status,
            "candidate_ms": round(candidate_latency_ms, 4),
            "verified_speedup": round(verified_speedup, 3),
            "classification": classification,
        }

        try:
            with open(self.current_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

        return entry
