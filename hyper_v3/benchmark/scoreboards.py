"""
hyper_v3/benchmark/scoreboards.py
Maintains four isolated scientific scoreboards:
- SCOREBOARD A: Exact Computation (EPS)
- SCOREBOARD B: Contract-Aware Computation (CPS)
- SCOREBOARD C: Computation Elimination (VWA, CES, Work Ledger)
- SCOREBOARD D: Hardware Execution (CPU/iGPU %, Memory & Transfer Traffic)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class ScoreboardAEntry:
    workload_name: str
    exact_passed: bool
    reference_time_us: float
    actual_time_us: float
    max_relative_error: float


@dataclass
class ScoreboardBEntry:
    workload_name: str
    contract_passed: bool
    contract_time_us: float
    verified_work_avoidance: float
    error_observed: float
    error_threshold: float


@dataclass
class ScoreboardCEntry:
    workload_name: str
    reference_flops: int
    eliminated_flops: int
    transformed_flops: int
    executed_flops: int
    verified_work_avoidance: float
    double_counting_prevented: bool = True


@dataclass
class ScoreboardDEntry:
    workload_name: str
    target_device: str
    cpu_percent: float
    igpu_percent: float
    memory_traffic_bytes: int
    transfer_traffic_bytes: int
    latency_us: float


class ScoreboardManager:
    """Aggregates and formats data across all 4 independent scoreboards."""

    def __init__(self):
        self.scoreboard_a: List[ScoreboardAEntry] = []
        self.scoreboard_b: List[ScoreboardBEntry] = []
        self.scoreboard_c: List[ScoreboardCEntry] = []
        self.scoreboard_d: List[ScoreboardDEntry] = []

    def compute_summary(self) -> Dict[str, Any]:
        total_a = len(self.scoreboard_a)
        passed_a = sum(1 for e in self.scoreboard_a if e.exact_passed)
        eps = (passed_a / total_a) if total_a > 0 else 1.0

        total_b = len(self.scoreboard_b)
        passed_b = sum(1 for e in self.scoreboard_b if e.contract_passed)
        cps = (passed_b / total_b) if total_b > 0 else 1.0

        avg_vwa = (sum(e.verified_work_avoidance for e in self.scoreboard_c) / len(self.scoreboard_c)) if self.scoreboard_c else 0.0

        return {
            "exact_parity_score": eps,
            "contract_parity_score": cps,
            "mean_verified_work_avoidance": avg_vwa,
            "total_workloads_evaluated": total_b
        }
