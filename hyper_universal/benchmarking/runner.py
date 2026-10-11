"""
hyper_universal/benchmarking/runner.py
Rigorous Real-Time and Sustained Performance Benchmarking Framework:
Preserves raw timing samples, computes p50/p95/p99 latency distributions,
tracks memory usage, and measures deadline-miss rates.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import numpy as np


import tracemalloc
import psutil


@dataclass
class BenchmarkDistributionReport:
    workload_id: str
    trials: int
    raw_samples_ms: List[float]
    median_ms: float
    mean_ms: float
    std_dev_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float
    deadline_miss_rate: float
    peak_memory_bytes: int
    reference_median_ms: float
    measured_speedup: float
    warmup_cost_ms: float = 0.0
    initialization_cost_ms: float = 0.0
    sustained_throughput_ops_sec: float = 0.0
    empirical_vs_worst_case_ratio: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "trials": self.trials,
            "median_ms": round(self.median_ms, 3),
            "mean_ms": round(self.mean_ms, 3),
            "std_dev_ms": round(self.std_dev_ms, 3),
            "p50_ms": round(self.p50_ms, 3),
            "p95_ms": round(self.p95_ms, 3),
            "p99_ms": round(self.p99_ms, 3),
            "min_ms": round(self.min_ms, 3),
            "max_ms": round(self.max_ms, 3),
            "deadline_miss_rate": round(self.deadline_miss_rate, 4),
            "peak_memory_bytes": self.peak_memory_bytes,
            "peak_memory_mb": round(self.peak_memory_bytes / (1024 * 1024), 2),
            "reference_median_ms": round(self.reference_median_ms, 3),
            "measured_speedup": round(self.measured_speedup, 2),
            "warmup_cost_ms": round(self.warmup_cost_ms, 3),
            "initialization_cost_ms": round(self.initialization_cost_ms, 3),
            "sustained_throughput_ops_sec": round(self.sustained_throughput_ops_sec, 1),
            "empirical_vs_worst_case_ratio": round(self.empirical_vs_worst_case_ratio, 2),
        }


class RigorousPerformanceBenchmarker:
    """Measures latency distributions, memory usage, and throughput across repeated trials."""

    @staticmethod
    def benchmark_workload(
        workload_id: str,
        kernel_fn: Callable[[Any], Any],
        sample_input: Any,
        reference_fn: Optional[Callable[[Any], Any]] = None,
        trials: int = 5,
        deadline_ms: Optional[float] = None,
    ) -> BenchmarkDistributionReport:
        tracemalloc.start()

        # Measure Warmup & Initialization Cost
        t_init_0 = time.perf_counter()
        try:
            _ = kernel_fn(sample_input)
            warmup_cost = (time.perf_counter() - t_init_0) * 1000.0
        except Exception:
            warmup_cost = 0.0

        # Reference timing if provided
        ref_median_ms = 0.0
        if reference_fn:
            ref_samples = []
            for _ in range(trials):
                t0 = time.perf_counter()
                _ = reference_fn(sample_input)
                ref_samples.append((time.perf_counter() - t0) * 1000.0)
            ref_median_ms = float(np.median(ref_samples))

        # Repeated candidate trials
        samples_ms: List[float] = []
        for _ in range(trials):
            t0 = time.perf_counter()
            _ = kernel_fn(sample_input)
            samples_ms.append((time.perf_counter() - t0) * 1000.0)

        current_bytes, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        arr = np.array(samples_ms)
        median_ms = float(np.median(arr))
        mean_ms = float(np.mean(arr))
        std_dev_ms = float(np.std(arr))
        p50 = float(np.percentile(arr, 50))
        p95 = float(np.percentile(arr, 95))
        p99 = float(np.percentile(arr, 99))
        min_ms = float(np.min(arr))
        max_ms = float(np.max(arr))

        miss_rate = 0.0
        if deadline_ms is not None and deadline_ms > 0:
            misses = sum(1 for s in samples_ms if s > deadline_ms)
            miss_rate = misses / float(trials)

        speedup = (ref_median_ms / median_ms) if (ref_median_ms > 0 and median_ms > 0) else 1.0
        throughput = (1000.0 / median_ms) if median_ms > 0 else 0.0
        worst_case_ratio = (max_ms / median_ms) if median_ms > 0 else 1.0

        return BenchmarkDistributionReport(
            workload_id=workload_id,
            trials=trials,
            raw_samples_ms=[round(s, 3) for s in samples_ms],
            median_ms=median_ms,
            mean_ms=mean_ms,
            std_dev_ms=std_dev_ms,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            min_ms=min_ms,
            max_ms=max_ms,
            deadline_miss_rate=miss_rate,
            peak_memory_bytes=peak_bytes,
            reference_median_ms=ref_median_ms,
            measured_speedup=speedup,
            warmup_cost_ms=warmup_cost,
            initialization_cost_ms=warmup_cost,
            sustained_throughput_ops_sec=throughput,
            empirical_vs_worst_case_ratio=worst_case_ratio,
        )
