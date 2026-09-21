"""
hyper/escape_engine/reporting/result_schema.py
=============================================
VAEE Section 27: Canonical Benchmark Result Schema.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class VerificationResultRecord:
    status: str                       # EXACT_VERIFIED | NUMERICALLY_VERIFIED | INVARIANT_VERIFIED | FAILED
    method: str
    error: float = 0.0
    relative_error: float = 0.0


@dataclasses.dataclass
class ExecutionResultRecord:
    device: str                       # "CPU_AVX2" | "INTEL_UHD_48EU" | "CPU+iGPU"
    latency_ms: float
    cpu_percent: float = 0.0
    igpu_percent: float = 0.0
    memory_mb: float = 0.0
    power_w: float = 35.0
    temperature_c: float = 55.0


@dataclasses.dataclass
class SearchResultRecord:
    candidate_index: int
    total_candidates: int
    structurally_unique: bool
    generation_depth: int
    saturation_detected: bool = False


@dataclasses.dataclass
class BenchmarkResult:
    experiment_id: str
    workload: str
    contract: str
    pathway_id: str
    algorithm_family: str
    verification: VerificationResultRecord
    execution: ExecutionResultRecord
    search: SearchResultRecord
    classification: str               # "SUCCESS" | "FAILURE" | "UNKNOWN" | "BARRIER"
    speedup_vs_baseline: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "workload": self.workload,
            "contract": self.contract,
            "pathway_id": self.pathway_id,
            "algorithm_family": self.algorithm_family,
            "verification": dataclasses.asdict(self.verification),
            "execution": dataclasses.asdict(self.execution),
            "search": dataclasses.asdict(self.search),
            "classification": self.classification,
            "speedup_vs_baseline": round(self.speedup_vs_baseline, 2),
        }
