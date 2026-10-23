"""
hyper/canonical/benchmark_harness.py
====================================
Honest Multi-Run Statistical Benchmark Harness.

Measures real execution latencies and memory consumption over repeated runs.
Maintains absolute separation between correctness verification and performance.
Strictly disallows simulated GPU latencies or fabricated acceleration metrics.
"""

from __future__ import annotations

import dataclasses
import statistics
import time
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.canonical.workload_registry import (
    CanonicalWorkloadContract,
    CANONICAL_REGISTRY,
)
from hyper.canonical.independent_reference import IndependentReferenceEngine
from hyper.canonical.candidate_compiler import CandidateCompiler
from hyper.canonical.verification_state_machine import StrictVerificationRunner
from hyper.canonical.hardware_backends import HARDWARE_BACKEND


@dataclasses.dataclass
class WorkloadBenchmarkRecord:
    """Statistical measurement record for a single workload."""
    workload_id: str
    backend_used: str
    warmup_runs: int
    measured_runs: int
    reference_median_ms: float
    reference_mean_ms: float
    reference_stddev_ms: float
    candidate_median_ms: float
    candidate_mean_ms: float
    candidate_stddev_ms: float
    speedup_vs_baseline: float
    peak_memory_bytes: int
    correctness_status: str
    discrete_gpu_parity_status: str = "NOT_MEASURED (No Discrete NVIDIA GPU present)"
    provenance: str = "LOCAL_EMPIRICAL_BENCHMARK"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "backend_used": self.backend_used,
            "warmup_runs": self.warmup_runs,
            "measured_runs": self.measured_runs,
            "reference_median_ms": round(self.reference_median_ms, 4),
            "reference_mean_ms": round(self.reference_mean_ms, 4),
            "reference_stddev_ms": round(self.reference_stddev_ms, 4),
            "candidate_median_ms": round(self.candidate_median_ms, 4),
            "candidate_mean_ms": round(self.candidate_mean_ms, 4),
            "candidate_stddev_ms": round(self.candidate_stddev_ms, 4),
            "speedup_vs_baseline": round(self.speedup_vs_baseline, 2),
            "peak_memory_bytes": self.peak_memory_bytes,
            "correctness_status": self.correctness_status,
            "discrete_gpu_parity_status": self.discrete_gpu_parity_status,
            "provenance": self.provenance,
        }


@dataclasses.dataclass
class SuiteBenchmarkReport:
    """Full benchmark results across all canonical workloads."""
    workloads_measured: int
    records: Dict[str, WorkloadBenchmarkRecord]
    hardware_summary: Dict[str, Any]
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workloads_measured": self.workloads_measured,
            "records": {k: v.to_dict() for k, v in self.records.items()},
            "hardware_summary": self.hardware_summary,
            "timestamp": self.timestamp,
        }


class HonestBenchmarkHarness:
    """
    Executes rigorous statistical timing and memory benchmarks.
    """

    @classmethod
    def benchmark_workload(
        cls,
        workload_id: str,
        warmup_runs: int = 2,
        measured_runs: int = 5,
        prefer_igpu: bool = True,
    ) -> WorkloadBenchmarkRecord:
        """Runs warmup + repeated timing measurements for candidate vs reference."""
        contract = CANONICAL_REGISTRY.get(workload_id)
        if contract is None:
            raise ValueError(f"Unknown workload: {workload_id}")

        inputs = StrictVerificationRunner.generate_typical_inputs(workload_id, seed=42)

        # -------------------------------------------------------------
        # 1. Reference Timing
        # -------------------------------------------------------------
        # Warmup
        for _ in range(warmup_runs):
            IndependentReferenceEngine.execute_reference(workload_id, inputs)

        ref_times: List[float] = []
        for _ in range(measured_runs):
            t0 = time.perf_counter()
            ref_out, _ = IndependentReferenceEngine.execute_reference(workload_id, inputs)
            ref_times.append((time.perf_counter() - t0) * 1000.0)

        ref_median = float(statistics.median(ref_times))
        ref_mean = float(statistics.mean(ref_times))
        ref_stddev = float(statistics.stdev(ref_times)) if len(ref_times) > 1 else 0.0

        # -------------------------------------------------------------
        # 2. Candidate Timing & Memory Profiling
        # -------------------------------------------------------------
        target_backend = "INTEL_UHD_IGPU" if (prefer_igpu and workload_id == "GEMM_STANDARD") else "CPU_AVX2"

        # Warmup
        for _ in range(warmup_runs):
            CandidateCompiler.execute_candidate(workload_id, inputs, contract=contract, target_backend=target_backend)

        cand_times: List[float] = []
        actual_backend = target_backend
        cand_out = None

        tracemalloc.start()
        tracemalloc.reset_peak()

        for _ in range(measured_runs):
            t0 = time.perf_counter()
            cand_out, cand_rec = CandidateCompiler.execute_candidate(workload_id, inputs, contract=contract, target_backend=target_backend)
            cand_times.append((time.perf_counter() - t0) * 1000.0)
            actual_backend = cand_rec.selected_backend

        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        cand_median = float(statistics.median(cand_times))
        cand_mean = float(statistics.mean(cand_times))
        cand_stddev = float(statistics.stdev(cand_times)) if len(cand_times) > 1 else 0.0

        # Output compliance check
        ok, status_msg, _ = contract.check_output_compliance(cand_out, ref_out)
        correctness_status = "VERIFIED_CORRECT" if ok else f"FAILED_VERIFICATION: {status_msg}"

        speedup = ref_median / max(0.0001, cand_median)

        return WorkloadBenchmarkRecord(
            workload_id=workload_id,
            backend_used=actual_backend,
            warmup_runs=warmup_runs,
            measured_runs=measured_runs,
            reference_median_ms=ref_median,
            reference_mean_ms=ref_mean,
            reference_stddev_ms=ref_stddev,
            candidate_median_ms=cand_median,
            candidate_mean_ms=cand_mean,
            candidate_stddev_ms=cand_stddev,
            speedup_vs_baseline=speedup,
            peak_memory_bytes=peak_mem,
            correctness_status=correctness_status,
        )

    @classmethod
    def benchmark_canonical_suite(
        cls,
        warmup_runs: int = 2,
        measured_runs: int = 5,
        prefer_igpu: bool = True,
    ) -> SuiteBenchmarkReport:
        """Runs empirical benchmarks across all 15 workloads."""
        records: Dict[str, WorkloadBenchmarkRecord] = {}
        for wid in CANONICAL_REGISTRY.list_workloads():
            rec = cls.benchmark_workload(wid, warmup_runs=warmup_runs, measured_runs=measured_runs, prefer_igpu=prefer_igpu)
            records[wid] = rec

        return SuiteBenchmarkReport(
            workloads_measured=len(records),
            records=records,
            hardware_summary=HARDWARE_BACKEND.profile.to_dict(),
        )
