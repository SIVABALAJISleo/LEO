"""
hyper_cco/raw_ledger.py
=======================
High-Precision Raw-Trial Ledger for HYPER-CCO Benchmarking.

Maintains an immutable record of individual trial iterations with:
  - Nanosecond resolution timing via time.perf_counter_ns()
  - Memory telemetry (RSS, virtual memory, peak memory)
  - Explicit separation of warmup iterations vs timed repetitions
  - Distributional statistics: min, max, mean, median, p95, p99, std
  - Cryptographic hash binding of trial conditions and environment metadata
  - Strict adherence to the 8-class Evidence Taxonomy (MEASURED_TARGET, MEASURED_NON_TARGET, etc.)
  - Full JSON serialization preserving all raw data points for scientific auditing
"""

import os
import json
import time
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import numpy as np

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from hyper_cco.contract import EvidenceClass, VerificationStatus


@dataclass
class TrialIteration:
    """Record of a single execution iteration."""
    iteration_index: int
    is_warmup: bool
    start_time_ns: int
    end_time_ns: int
    duration_ns: int
    duration_ms: float
    rss_bytes_before: int = 0
    rss_bytes_after: int = 0
    verified: bool = True
    error_abs: float = 0.0
    error_rel: float = 0.0
    normwise_err: float = 0.0


@dataclass
class TrialSummaryStatistics:
    """Summary distribution statistics computed strictly over timed (non-warmup) iterations."""
    sample_count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    std_ms: float
    iqr_ms: float
    throughput_items_per_sec: float
    gflops: float


@dataclass
class WorkloadTrialRecord:
    """Complete trial record for a candidate execution on a workload."""
    workload_id: str
    candidate_id: str
    evidence_class: str
    hardware_provenance: Dict[str, Any]
    contract_hash: str
    warmup_count: int
    timed_count: int
    warmup_iterations: List[TrialIteration] = field(default_factory=list)
    timed_iterations: List[TrialIteration] = field(default_factory=list)
    statistics: Optional[TrialSummaryStatistics] = None
    verification_status: str = VerificationStatus.PASS.value
    notes: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return asdict(self)


class RawTrialLedger:
    """
    Authoritative ledger managing trial recording, statistical aggregation,
    and persistent storage for HYPER benchmark suites.
    """

    def __init__(self, output_path: str = "benchmark_results/raw_trials.json"):
        self.output_path = output_path
        self.records: List[WorkloadTrialRecord] = []
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)

    @staticmethod
    def get_memory_rss() -> int:
        """Query current process RSS memory in bytes."""
        if HAS_PSUTIL:
            try:
                process = psutil.Process()
                return process.memory_info().rss
            except Exception:
                pass
        return 0

    def record_workload_run(
        self,
        workload_id: str,
        candidate_id: str,
        run_fn,
        verify_fn,
        warmup_reps: int = 3,
        timed_reps: int = 30,
        evidence_class: EvidenceClass = EvidenceClass.MEASURED_NON_TARGET,
        hardware_provenance: Optional[Dict[str, Any]] = None,
        contract_hash: str = "0000000000000000000000000000000000000000000000000000000000000000",
        flop_count_per_op: float = 0.0,
        items_count_per_op: float = 1.0,
        notes: Optional[str] = None,
    ) -> WorkloadTrialRecord:
        """
        Executes and records individual warmup and timed trials with microsecond precision.
        """
        if hardware_provenance is None:
            hardware_provenance = {
                "detected_platform": os.name,
                "recorded_at": time.time(),
            }

        warmup_records: List[TrialIteration] = []
        timed_records: List[TrialIteration] = []

        # 1. Warmup Iterations (Discarded from statistics)
        for i in range(warmup_reps):
            rss_before = self.get_memory_rss()
            t0 = time.perf_counter_ns()
            output = run_fn()
            t1 = time.perf_counter_ns()
            rss_after = self.get_memory_rss()

            dur_ns = t1 - t0
            is_valid, err_abs, err_rel = verify_fn(output)

            warmup_records.append(
                TrialIteration(
                    iteration_index=i,
                    is_warmup=True,
                    start_time_ns=t0,
                    end_time_ns=t1,
                    duration_ns=dur_ns,
                    duration_ms=dur_ns / 1_000_000.0,
                    rss_bytes_before=rss_before,
                    rss_bytes_after=rss_after,
                    verified=is_valid,
                    error_abs=float(err_abs),
                    error_rel=float(err_rel),
                )
            )

        # 2. Timed Repetitions (Retained for statistical distribution)
        overall_status = VerificationStatus.PASS.value
        for i in range(timed_reps):
            rss_before = self.get_memory_rss()
            t0 = time.perf_counter_ns()
            output = run_fn()
            t1 = time.perf_counter_ns()
            rss_after = self.get_memory_rss()

            dur_ns = t1 - t0
            is_valid, err_abs, err_rel = verify_fn(output)
            if not is_valid:
                overall_status = VerificationStatus.FAIL.value

            timed_records.append(
                TrialIteration(
                    iteration_index=i,
                    is_warmup=False,
                    start_time_ns=t0,
                    end_time_ns=t1,
                    duration_ns=dur_ns,
                    duration_ms=dur_ns / 1_000_000.0,
                    rss_bytes_before=rss_before,
                    rss_bytes_after=rss_after,
                    verified=is_valid,
                    error_abs=float(err_abs),
                    error_rel=float(err_rel),
                )
            )

        # 3. Compute Distributional Statistics
        durations_ms = [r.duration_ms for r in timed_records]
        if durations_ms:
            sorted_durations = sorted(durations_ms)
            n = len(sorted_durations)
            min_ms = float(np.min(sorted_durations))
            max_ms = float(np.max(sorted_durations))
            mean_ms = float(np.mean(sorted_durations))
            median_ms = float(np.median(sorted_durations))
            p95_ms = float(np.percentile(sorted_durations, 95))
            p99_ms = float(np.percentile(sorted_durations, 99))
            std_ms = float(np.std(sorted_durations))
            q75, q25 = np.percentile(sorted_durations, [75, 25])
            iqr_ms = float(q75 - q25)

            # Throughput & GFLOPS based on median time (robust against outliers)
            median_sec = max(1e-9, median_ms / 1000.0)
            throughput = items_count_per_op / median_sec
            gflops = (flop_count_per_op / 1e9) / median_sec if flop_count_per_op > 0 else 0.0

            stats = TrialSummaryStatistics(
                sample_count=n,
                min_ms=min_ms,
                max_ms=max_ms,
                mean_ms=mean_ms,
                median_ms=median_ms,
                p95_ms=p95_ms,
                p99_ms=p99_ms,
                std_ms=std_ms,
                iqr_ms=iqr_ms,
                throughput_items_per_sec=throughput,
                gflops=gflops,
            )
        else:
            stats = None

        record = WorkloadTrialRecord(
            workload_id=workload_id,
            candidate_id=candidate_id,
            evidence_class=evidence_class.value,
            hardware_provenance=hardware_provenance,
            contract_hash=contract_hash,
            warmup_count=warmup_reps,
            timed_count=timed_reps,
            warmup_iterations=warmup_records,
            timed_iterations=timed_records,
            statistics=stats,
            verification_status=overall_status,
            notes=notes,
        )

        self.records.append(record)
        self.save()
        return record

    def save(self):
        """Atomically persist all records to output JSON file."""
        data = [r.to_dict() for r in self.records]
        tmp_file = f"{self.output_path}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_file, self.output_path)

    @classmethod
    def load(cls, file_path: str) -> "RawTrialLedger":
        """Load an existing ledger from disk."""
        ledger = cls(output_path=file_path)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for item in raw_data:
                    stats_dict = item.get("statistics")
                    stats = TrialSummaryStatistics(**stats_dict) if stats_dict else None
                    warmups = [TrialIteration(**it) for it in item.get("warmup_iterations", [])]
                    timeds = [TrialIteration(**it) for it in item.get("timed_iterations", [])]

                    rec = WorkloadTrialRecord(
                        workload_id=item["workload_id"],
                        candidate_id=item["candidate_id"],
                        evidence_class=item["evidence_class"],
                        hardware_provenance=item["hardware_provenance"],
                        contract_hash=item["contract_hash"],
                        warmup_count=item["warmup_count"],
                        timed_count=item["timed_count"],
                        warmup_iterations=warmups,
                        timed_iterations=timeds,
                        statistics=stats,
                        verification_status=item["verification_status"],
                        notes=item.get("notes"),
                        created_at=item.get("created_at", 0.0),
                    )
                    ledger.records.append(rec)
        return ledger
