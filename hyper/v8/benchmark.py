"""
hyper/v8/benchmark.py
=====================
HYPER v8 — BenchmarkHarnessV2 + BenchmarkResult.

Provenance-complete benchmarking with strict separation of cold vs warm timing.
All measurements use time.perf_counter_ns().
Never mix cold GPU dispatch/cache with warm kernel runs.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .contract import PathClassification, VerificationStatus
from .scheduler import probe_hardware


def _get_git_commit() -> str:
    """Retrieve current git commit hash."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out
    except Exception:
        return "UNKNOWN_COMMIT"


@dataclasses.dataclass
class BenchmarkResult:
    """
    Complete scientific record of a benchmark measurement.
    Adheres strictly to the HYPER v8 measurement protocol.
    """
    algorithm: str
    path_type: PathClassification
    problem_size: Tuple[int, ...]
    input_digest: str
    warmup_count: int
    measurement_count: int
    cold_start_ms: float
    warm_start_ms: float
    median_ms: float
    mean_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float
    std_ms: float
    reference_median_ms: float
    speedup_vs_baseline: float
    work_eliminated_pct: float
    verification_status: VerificationStatus
    hardware_identity: str
    git_commit: str
    result_classification: str = "MEASURED"
    energy_joules: Optional[float] = None  # None = NOT_MEASURED (no physical sensor)
    timestamp: float = dataclasses.field(default_factory=time.time)
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "path_type": self.path_type.value,
            "problem_size": list(self.problem_size),
            "input_digest": self.input_digest[:16] + "...",
            "warmup_count": self.warmup_count,
            "measurement_count": self.measurement_count,
            "cold_start_ms": round(self.cold_start_ms, 4),
            "warm_start_ms": round(self.warm_start_ms, 4),
            "median_ms": round(self.median_ms, 4),
            "mean_ms": round(self.mean_ms, 4),
            "p95_ms": round(self.p95_ms, 4),
            "p99_ms": round(self.p99_ms, 4),
            "min_ms": round(self.min_ms, 4),
            "max_ms": round(self.max_ms, 4),
            "std_ms": round(self.std_ms, 4),
            "reference_median_ms": round(self.reference_median_ms, 4),
            "speedup_vs_baseline": round(self.speedup_vs_baseline, 2),
            "work_eliminated_pct": round(self.work_eliminated_pct, 2),
            "verification_status": self.verification_status.value,
            "result_classification": self.result_classification,
            "energy_joules": "NOT_MEASURED" if self.energy_joules is None else self.energy_joules,
            "hardware_identity": self.hardware_identity,
            "git_commit": self.git_commit[:8],
            "notes": self.notes,
        }


class BenchmarkHarnessV2:
    """
    Standardized benchmark harness for HYPER v8.
    Strictly separates cold starts, warms up caches deterministically,
    and calculates statistical percentiles.
    """

    def __init__(self, warmup_runs: int = 3, measurement_runs: int = 10) -> None:
        self.warmup_runs = warmup_runs
        self.measurement_runs = measurement_runs
        self.cert = probe_hardware()
        self.hw_id = f"{self.cert.cpu_model} ({self.cert.cpu_cores_physical}P/{self.cert.cpu_cores_logical}T) | {self.cert.igpu_name} | {self.cert.ram_gb:.1f}GB RAM"
        self.git_commit = _get_git_commit()

    def benchmark(
        self,
        name: str,
        fn: Callable[[], Any],
        ref_fn: Optional[Callable[[], Any]] = None,
        path_type: PathClassification = PathClassification.EXACT_FRESH,
        problem_size: Tuple[int, ...] = (),
        input_digest: str = "",
        verification_status: VerificationStatus = VerificationStatus.VERIFIED_EXACT,
        work_eliminated_pct: float = 0.0,
        notes: str = "",
    ) -> BenchmarkResult:
        """
        Run isolated benchmark on `fn`. If `ref_fn` is provided, also measures baseline.
        """
        # 1. Cold start measurement
        t0 = time.perf_counter_ns()
        _ = fn()
        cold_start_ms = (time.perf_counter_ns() - t0) / 1e6

        # 2. Warmup passes
        for _ in range(self.warmup_runs):
            fn()

        # 3. Measurement runs (warm)
        warm_times = []
        for _ in range(self.measurement_runs):
            t0 = time.perf_counter_ns()
            fn()
            warm_times.append((time.perf_counter_ns() - t0) / 1e6)

        warm_times = np.array(warm_times, dtype=np.float64)
        median_ms = float(np.median(warm_times))
        mean_ms = float(np.mean(warm_times))
        p95_ms = float(np.percentile(warm_times, 95))
        p99_ms = float(np.percentile(warm_times, 99))
        min_ms = float(np.min(warm_times))
        max_ms = float(np.max(warm_times))
        std_ms = float(np.std(warm_times))
        warm_start_ms = float(warm_times[0])

        # 4. Measure baseline reference if provided
        ref_median_ms = median_ms
        if ref_fn is not None:
            # Warmup ref
            for _ in range(self.warmup_runs):
                ref_fn()
            ref_times = []
            for _ in range(self.measurement_runs):
                t0 = time.perf_counter_ns()
                ref_fn()
                ref_times.append((time.perf_counter_ns() - t0) / 1e6)
            ref_median_ms = float(np.median(ref_times))

        speedup = ref_median_ms / max(1e-9, median_ms)

        return BenchmarkResult(
            algorithm=name,
            path_type=path_type,
            problem_size=problem_size,
            input_digest=input_digest or "na",
            warmup_count=self.warmup_runs,
            measurement_count=self.measurement_runs,
            cold_start_ms=cold_start_ms,
            warm_start_ms=warm_start_ms,
            median_ms=median_ms,
            mean_ms=mean_ms,
            p95_ms=p95_ms,
            p99_ms=p99_ms,
            min_ms=min_ms,
            max_ms=max_ms,
            std_ms=std_ms,
            reference_median_ms=ref_median_ms,
            speedup_vs_baseline=speedup,
            work_eliminated_pct=work_eliminated_pct,
            verification_status=verification_status,
            hardware_identity=self.hw_id,
            git_commit=self.git_commit,
            result_classification="MEASURED",
            energy_joules=None,  # Physically not measured on this laptop
            notes=notes,
        )
