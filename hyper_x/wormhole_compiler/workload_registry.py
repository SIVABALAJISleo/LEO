"""
hyper_x/wormhole_compiler/workload_registry.py
=============================================================================
Universal Workload Registry & Workload Closure Engine (Section 36 & 63)
=============================================================================
Tracks every evaluated workload across the universal benchmark universe:
  - Dense Linear Algebra
  - Sparse Linear Algebra
  - AI / LLM Inference
  - Transformer Attention / KV Cache
  - Computer Vision / CNN
  - Graphics / Temporal Denoising / Path Tracing
  - Scientific Stencils / PDE
  - Database Query Filtering & Aggregation
  - RAG Embedding Search

Every workload MUST be classified into one of three mutually exclusive outcomes:
  1. WORMHOLE_FOUND: A verified computational shortcut exists under the contract.
  2. NECESSARY_COMPUTATION_PROVEN: Computation cannot be removed; lower bound reached.
  3. SEARCH_INCONCLUSIVE: Current search could neither find a valid shortcut nor prove necessity.

Universal Workload Closure Metric:
  Closure = (wormholes_found + necessity_proven) / total_evaluated_workloads

100% Workload Closure can ONLY be claimed if:
  inconclusive == 0 and every evaluated workload has valid hardware provenance.
"""

from __future__ import annotations
import json
import time
import enum
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


class WorkloadOutcome(str, enum.Enum):
    WORMHOLE_FOUND = "WORMHOLE_FOUND"
    NECESSARY_COMPUTATION_PROVEN = "NECESSARY_COMPUTATION_PROVEN"
    SEARCH_INCONCLUSIVE = "SEARCH_INCONCLUSIVE"


@dataclass
class WorkloadRegistryEntry:
    workload_id: str
    domain: str
    contract_mode: str
    observable: str
    outcome: WorkloadOutcome
    speedup: float
    work_elimination_ratio: float
    gadr: float
    hae: float
    provenance_verified: bool
    holdout_passed: bool
    exact_correctness: bool
    contract_correctness: bool
    timestamp: float = field(default_factory=time.time)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["outcome"] = self.outcome.value
        return d


@dataclass
class UniversalClosureScorecard:
    total_evaluated_workloads: int
    wormholes_found: int
    necessity_proven: int
    inconclusive_searches: int
    closure_ratio: float  # (wormholes + necessity) / total

    # Multi-dimensional separate metrics (Never combined into one number)
    exact_correctness_ratio: float
    contract_correctness_ratio: float
    holdout_coverage_ratio: float
    provenance_coverage_ratio: float
    hardware_advantage_erasure_mean: float
    mean_speedup: float
    can_claim_100_percent_closure: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_evaluated_workloads": self.total_evaluated_workloads,
            "wormholes_found": self.wormholes_found,
            "necessity_proven": self.necessity_proven,
            "inconclusive_searches": self.inconclusive_searches,
            "closure_percentage": f"{self.closure_ratio * 100:.2f}%",
            "can_claim_100_percent_closure": self.can_claim_100_percent_closure,
            "metrics_breakdown": {
                "exact_correctness": f"{self.exact_correctness_ratio * 100:.2f}%",
                "contract_correctness": f"{self.contract_correctness_ratio * 100:.2f}%",
                "holdout_coverage": f"{self.holdout_coverage_ratio * 100:.2f}%",
                "provenance_coverage": f"{self.provenance_coverage_ratio * 100:.2f}%",
                "hardware_advantage_erasure_mean": f"{self.hardware_advantage_erasure_mean * 100:.2f}%",
                "mean_speedup": f"{self.mean_speedup:.2f}x",
            }
        }


class UniversalWorkloadRegistry:
    """
    Registry maintaining all benchmark workload outcomes and computing objective closure.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("workload_registry.json")
        self.entries: Dict[str, WorkloadRegistryEntry] = {}
        self.load_if_exists()

    def register(self, entry: WorkloadRegistryEntry):
        self.entries[entry.workload_id] = entry
        self.save()

    def compute_closure(self) -> UniversalClosureScorecard:
        total = len(self.entries)
        if total == 0:
            return UniversalClosureScorecard(
                total_evaluated_workloads=0,
                wormholes_found=0,
                necessity_proven=0,
                inconclusive_searches=0,
                closure_ratio=0.0,
                exact_correctness_ratio=0.0,
                contract_correctness_ratio=0.0,
                holdout_coverage_ratio=0.0,
                provenance_coverage_ratio=0.0,
                hardware_advantage_erasure_mean=0.0,
                mean_speedup=1.0,
                can_claim_100_percent_closure=False,
            )

        wormholes = sum(1 for e in self.entries.values() if e.outcome == WorkloadOutcome.WORMHOLE_FOUND)
        necessity = sum(1 for e in self.entries.values() if e.outcome == WorkloadOutcome.NECESSARY_COMPUTATION_PROVEN)
        inconclusive = sum(1 for e in self.entries.values() if e.outcome == WorkloadOutcome.SEARCH_INCONCLUSIVE)

        closure = (wormholes + necessity) / total
        exact_ratio = sum(1 for e in self.entries.values() if e.exact_correctness) / total
        contract_ratio = sum(1 for e in self.entries.values() if e.contract_correctness) / total
        holdout_ratio = sum(1 for e in self.entries.values() if e.holdout_passed) / total
        prov_ratio = sum(1 for e in self.entries.values() if e.provenance_verified) / total
        hae_mean = sum(e.hae for e in self.entries.values()) / total
        mean_spd = sum(e.speedup for e in self.entries.values()) / total

        can_claim = (inconclusive == 0 and total > 0 and prov_ratio == 1.0 and holdout_ratio == 1.0)

        return UniversalClosureScorecard(
            total_evaluated_workloads=total,
            wormholes_found=wormholes,
            necessity_proven=necessity,
            inconclusive_searches=inconclusive,
            closure_ratio=closure,
            exact_correctness_ratio=exact_ratio,
            contract_correctness_ratio=contract_ratio,
            holdout_coverage_ratio=holdout_ratio,
            provenance_coverage_ratio=prov_ratio,
            hardware_advantage_erasure_mean=hae_mean,
            mean_speedup=mean_spd,
            can_claim_100_percent_closure=can_claim,
        )

    def save(self):
        data = {k: v.to_dict() for k, v in self.entries.items()}
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_if_exists(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    self.entries[k] = WorkloadRegistryEntry(
                        workload_id=v["workload_id"],
                        domain=v["domain"],
                        contract_mode=v["contract_mode"],
                        observable=v["observable"],
                        outcome=WorkloadOutcome(v["outcome"]),
                        speedup=v["speedup"],
                        work_elimination_ratio=v["work_elimination_ratio"],
                        gadr=v["gadr"],
                        hae=v["hae"],
                        provenance_verified=v["provenance_verified"],
                        holdout_passed=v["holdout_passed"],
                        exact_correctness=v["exact_correctness"],
                        contract_correctness=v["contract_correctness"],
                        timestamp=v.get("timestamp", time.time()),
                        notes=v.get("notes", "")
                    )
            except Exception:
                pass
