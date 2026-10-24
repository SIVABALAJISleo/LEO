"""
hyper_phase_change/experiment_db.py
===================================
Research Memory & Failed-Attempt Learning Database.

Maintains structured, persistent logs of all algorithm discovery experiments,
hypotheses, empirical measurements, failure categorizations, and recommended next experiments.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class FailureCategory(str, Enum):
    NONE = "NONE"
    INCORRECT_OUTPUT = "INCORRECT_OUTPUT"
    NUMERICAL_INSTABILITY = "NUMERICAL_INSTABILITY"
    UNSUPPORTED_OPERATOR = "UNSUPPORTED_OPERATOR"
    MEMORY_OVERFLOW = "MEMORY_OVERFLOW"
    COMPILATION_FAILURE = "COMPILATION_FAILURE"
    RUNTIME_FAILURE = "RUNTIME_FAILURE"
    TRANSFER_OVERHEAD = "TRANSFER_OVERHEAD"
    OPTIMIZATION_OVERHEAD = "OPTIMIZATION_OVERHEAD"
    THERMAL_THROTTLING = "THERMAL_THROTTLING"
    NO_SPEEDUP = "NO_SPEEDUP"


@dataclasses.dataclass
class ExperimentRecord:
    experiment_id: str
    workload_id: str
    hypothesis: str
    baseline_backend: str
    baseline_latency_ms: float
    candidate_id: str
    candidate_transformation: str
    input_domain: Dict[str, Any]
    correctness_evidence: bool
    max_observed_error: float
    performance_evidence: bool
    candidate_latency_ms: float
    speedup: float
    environment: str
    result: str  # ACCEPTED or REJECTED
    failure_category: FailureCategory
    failure_details: Optional[str]
    next_experiment: str
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "workload_id": self.workload_id,
            "hypothesis": self.hypothesis,
            "baseline_backend": self.baseline_backend,
            "baseline_latency_ms": round(self.baseline_latency_ms, 4),
            "candidate_id": self.candidate_id,
            "candidate_transformation": self.candidate_transformation,
            "input_domain": self.input_domain,
            "correctness_evidence": self.correctness_evidence,
            "max_observed_error": float(self.max_observed_error),
            "performance_evidence": self.performance_evidence,
            "candidate_latency_ms": round(self.candidate_latency_ms, 4),
            "speedup": round(self.speedup, 4),
            "environment": self.environment,
            "result": self.result,
            "failure_category": self.failure_category.value,
            "failure_details": self.failure_details,
            "next_experiment": self.next_experiment,
            "timestamp": self.timestamp,
        }


class ResearchExperimentDB:
    """
    Local Research Memory and Experiment Tracking Engine.
    Stores and analyzes empirical hypotheses and failure modes to guide future candidate synthesis.
    """

    DEFAULT_DB_PATH = Path("reports/EXPERIMENT_DATABASE.jsonl")

    def __init__(self, db_path: Optional[Union[str, Path]] = None) -> None:
        self.db_path = Path(db_path) if db_path else self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[ExperimentRecord] = []
        self._load_existing()

    def _load_existing(self) -> None:
        if not self.db_path.exists():
            return
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    rec = ExperimentRecord(
                        experiment_id=data["experiment_id"],
                        workload_id=data["workload_id"],
                        hypothesis=data["hypothesis"],
                        baseline_backend=data["baseline_backend"],
                        baseline_latency_ms=data["baseline_latency_ms"],
                        candidate_id=data["candidate_id"],
                        candidate_transformation=data["candidate_transformation"],
                        input_domain=data["input_domain"],
                        correctness_evidence=data["correctness_evidence"],
                        max_observed_error=data["max_observed_error"],
                        performance_evidence=data["performance_evidence"],
                        candidate_latency_ms=data["candidate_latency_ms"],
                        speedup=data["speedup"],
                        environment=data["environment"],
                        result=data["result"],
                        failure_category=FailureCategory(data.get("failure_category", "NONE")),
                        failure_details=data.get("failure_details"),
                        next_experiment=data["next_experiment"],
                        timestamp=data.get("timestamp", time.time()),
                    )
                    self._records.append(rec)
        except Exception:
            pass

    def record_experiment(
        self,
        experiment_id: str,
        workload_id: str,
        hypothesis: str,
        baseline_backend: str,
        baseline_latency_ms: float,
        candidate_id: str,
        candidate_transformation: str,
        input_domain: Dict[str, Any],
        correctness_evidence: bool,
        max_observed_error: float,
        performance_evidence: bool,
        candidate_latency_ms: float,
        speedup: float,
        environment: str = "Lenovo Slim 3 15IAH8 | Intel i5-12450H + UHD iGPU 48 EUs | 16GB RAM | Windows 11",
        result: str = "ACCEPTED",
        failure_category: FailureCategory = FailureCategory.NONE,
        failure_details: Optional[str] = None,
        next_experiment: str = "Proceed to next candidate",
    ) -> ExperimentRecord:
        """Appends an experiment record to memory and JSONL storage."""
        rec = ExperimentRecord(
            experiment_id=experiment_id,
            workload_id=workload_id,
            hypothesis=hypothesis,
            baseline_backend=baseline_backend,
            baseline_latency_ms=baseline_latency_ms,
            candidate_id=candidate_id,
            candidate_transformation=candidate_transformation,
            input_domain=input_domain,
            correctness_evidence=correctness_evidence,
            max_observed_error=max_observed_error,
            performance_evidence=performance_evidence,
            candidate_latency_ms=candidate_latency_ms,
            speedup=speedup,
            environment=environment,
            result=result,
            failure_category=failure_category,
            failure_details=failure_details,
            next_experiment=next_experiment,
        )
        self._records.append(rec)
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec.to_dict()) + "\n")
        return rec

    def query_failures(self, category: Optional[FailureCategory] = None) -> List[ExperimentRecord]:
        """Queries recorded failures, optionally filtered by category."""
        return [
            r for r in self._records
            if r.result == "REJECTED" and (category is None or r.failure_category == category)
        ]

    def recommend_next_strategy(self, workload_id: str) -> str:
        """Analyzes historical failures for this workload to prioritize the next experiment."""
        workload_recs = [r for r in self._records if r.workload_id == workload_id]
        if not workload_recs:
            return "No prior history: start with Baseline AVX2 and Structural Decomposition."

        failures = [r for r in workload_recs if r.result == "REJECTED"]
        cat_counts: Dict[str, int] = {}
        for f in failures:
            cat_counts[f.failure_category.value] = cat_counts.get(f.failure_category.value, 0) + 1

        if cat_counts.get(FailureCategory.NUMERICAL_INSTABILITY.value, 0) > 0:
            return "Prior numerical instability detected: increase precision to FP32 or use incremental residual boosting."
        if cat_counts.get(FailureCategory.OPTIMIZATION_OVERHEAD.value, 0) > 0:
            return "Prior discovery overhead exceeded savings: activate Discovery Cost Guard and dispatch direct BLAS."
        if cat_counts.get(FailureCategory.NO_SPEEDUP.value, 0) > 0:
            return "Prior attempts showed no speedup: investigate frequency-domain FFT bypass or out-of-core tiling."

        return "Prior experiments verified: proceed to real application workload expansion."

    def generate_markdown_summary(self) -> str:
        """Generates a comprehensive scientific markdown summary of the experiment database."""
        total = len(self._records)
        accepted = sum(1 for r in self._records if r.result == "ACCEPTED")
        rejected = total - accepted

        lines = [
            "# LEO / HYPER RESEARCH EXPERIMENT DATABASE SUMMARY",
            f"**Total Experiments Recorded**: {total}  ",
            f"**Accepted**: {accepted} | **Rejected**: {rejected}  ",
            "",
            "## 1. Failure Categories Breakdown",
            "| Failure Category | Count | Typical Cause | Resolution |",
            "| :--- | :--- | :--- | :--- |",
        ]

        cat_counts: Dict[str, int] = {}
        for r in self._records:
            if r.result == "REJECTED":
                c = r.failure_category.value
                cat_counts[c] = cat_counts.get(c, 0) + 1

        causes = {
            "NUMERICAL_INSTABILITY": ("Static low-rank truncation truncating > contract tolerance", "Derived dynamic energy bound epsilon^2 / 4"),
            "OPTIMIZATION_OVERHEAD": ("Structural analysis on small matrices (<64x64) taking longer than compute", "Added Discovery Cost Guard bypassing small inputs"),
            "INCORRECT_OUTPUT": ("Missing transposition or stride stride handling in naive kernel", "Enforce full-operand canonical stride hashing"),
            "NO_SPEEDUP": ("Vectorized candidate matching BLAS performance without algorithmic reduction", "Pivot to orthogonal basis or sparse/FFT bypass"),
            "MEMORY_OVERFLOW": ("Attempting to allocate full matrix in core for out-of-core workload", "Enforce 2048x2048 memmap tile streaming"),
        }

        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            cause, res = causes.get(cat, ("Various runtime boundaries", "Adjusted candidate parameters"))
            lines.append(f"| `{cat}` | {count} | {cause} | {res} |")

        lines.extend([
            "",
            "## 2. Recent Experiment Log",
            "| Exp ID | Workload | Candidate | Result | Speedup | Max Error | Failure Reason |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for r in self._records[-15:]:
            res_icon = "PASS" if r.result == "ACCEPTED" else "FAIL"
            err_str = f"{r.max_observed_error:.2e}" if r.max_observed_error > 0 else "0.0"
            lines.append(f"| `{r.experiment_id}` | `{r.workload_id}` | `{r.candidate_id}` | `{res_icon}` | {r.speedup:.2f}x | {err_str} | {r.failure_details or 'None'} |")

        return "\n".join(lines)


# Global Database Instance
EXPERIMENT_DB = ResearchExperimentDB()
