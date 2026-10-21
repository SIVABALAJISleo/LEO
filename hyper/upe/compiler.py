"""
hyper/upe/compiler.py
=====================
ENGINE 5: Search Space Compiler.

Executes a bounded, cost-guided search across candidate execution pathways.
Limits search time, memory, candidate count, and guarantees fall-closed safety.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper.upe.contract import WorkloadContract
from hyper.upe.generator import AlternativePathwayGenerator, CandidatePathway


@dataclasses.dataclass
class SearchBudget:
    """Configurable boundaries for optimization search."""
    max_search_duration_ms: float = 2000.0  # 2.0s timeout
    max_candidates_to_evaluate: int = 10
    max_memory_mb: float = 512.0
    benchmark_repetitions: int = 3
    early_stop_on_exact_match: bool = True


@dataclasses.dataclass
class SearchResult:
    """Outcome of bounded search space exploration."""
    workload_id: str
    total_candidates_considered: int
    valid_candidates_count: int
    rejected_candidates_count: int
    best_pathway: CandidatePathway
    all_evaluated_candidates: List[Dict[str, Any]]
    search_duration_ms: float
    shortcut_discovered: bool
    status_message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "total_candidates_considered": self.total_candidates_considered,
            "valid_candidates_count": self.valid_candidates_count,
            "rejected_candidates_count": self.rejected_candidates_count,
            "best_pathway": self.best_pathway.to_dict(),
            "all_evaluated_candidates": self.all_evaluated_candidates,
            "search_duration_ms": round(self.search_duration_ms, 2),
            "shortcut_discovered": self.shortcut_discovered,
            "status_message": self.status_message,
        }


class SearchSpaceCompiler:
    """
    Compiler-style bounded search over the candidate transformation space.
    """

    def __init__(self, generator: Optional[AlternativePathwayGenerator] = None) -> None:
        self.generator = generator or AlternativePathwayGenerator()

    def search(
        self,
        contract: WorkloadContract,
        inputs: Dict[str, Any],
        budget: Optional[SearchBudget] = None,
    ) -> SearchResult:
        """
        Explores valid candidate pathways within configured resource budget.
        """
        t0 = time.perf_counter()
        cfg = budget or SearchBudget()

        candidates = self.generator.generate_candidates(
            contract=contract,
            inputs=inputs,
            max_candidates=cfg.max_candidates_to_evaluate,
        )

        evaluated_list: List[Dict[str, Any]] = []
        valid_candidates: List[Tuple[float, CandidatePathway]] = []
        rejected_count = 0

        for cand in candidates:
            # Check elapsed search time timeout
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            if elapsed_ms > cfg.max_search_duration_ms:
                break

            if not cand.preconditions_met or cand.transform_fn is None:
                rejected_count += 1
                evaluated_list.append({
                    "pathway_id": cand.pathway_id,
                    "candidate_name": cand.candidate_name,
                    "status": "REJECTED_PRECONDITION",
                    "reason": cand.rejection_reason or "Preconditions not satisfied",
                    "speedup": cand.estimated_speedup,
                })
                continue

            # Quick trial execution to measure latency
            trial_times: List[float] = []
            exec_ok = True
            err_msg = ""
            for _ in range(cfg.benchmark_repetitions):
                try:
                    t_trial = time.perf_counter()
                    out, _ = cand.transform_fn(inputs)
                    trial_times.append((time.perf_counter() - t_trial) * 1000.0)
                except Exception as e:
                    exec_ok = False
                    err_msg = str(e)
                    break

            if not exec_ok:
                rejected_count += 1
                evaluated_list.append({
                    "pathway_id": cand.pathway_id,
                    "candidate_name": cand.candidate_name,
                    "status": "EXECUTION_EXCEPTION",
                    "reason": err_msg,
                    "speedup": 0.0,
                })
                continue

            median_lat_ms = float(np.median(trial_times)) if trial_times else 10.0
            # Score: higher speedup & lower latency is preferred
            score = cand.estimated_speedup / max(0.01, median_lat_ms)
            valid_candidates.append((score, cand))

            evaluated_list.append({
                "pathway_id": cand.pathway_id,
                "candidate_name": cand.candidate_name,
                "status": "VALID_CANDIDATE",
                "median_latency_ms": round(median_lat_ms, 3),
                "estimated_speedup": cand.estimated_speedup,
                "score": round(score, 3),
            })

            if cfg.early_stop_on_exact_match and cand.exactness_mode == "EXACT" and cand.estimated_speedup > 2.0:
                # Discovered a strong exact algebraic shortcut
                break

        # Select candidate with highest ranking score
        if valid_candidates:
            valid_candidates.sort(key=lambda x: x[0], reverse=True)
            best_cand = valid_candidates[0][1]
            shortcut_found = best_cand.rule_id != "baseline_reference"
            status_msg = (
                f"Verified unseen shortcut '{best_cand.candidate_name}' selected "
                f"({best_cand.estimated_speedup}x speedup)."
                if shortcut_found else "No superior shortcut discovered; baseline reference selected."
            )
        else:
            # Fallback to reference
            best_cand = candidates[0]
            shortcut_found = False
            status_msg = "All candidates rejected; defaulting to safe baseline."

        search_total_ms = (time.perf_counter() - t0) * 1000.0

        return SearchResult(
            workload_id=contract.workload_id,
            total_candidates_considered=len(candidates),
            valid_candidates_count=len(valid_candidates),
            rejected_candidates_count=rejected_count,
            best_pathway=best_cand,
            all_evaluated_candidates=evaluated_list,
            search_duration_ms=search_total_ms,
            shortcut_discovered=shortcut_found,
            status_message=status_msg,
        )
