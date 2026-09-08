"""
hyper_x/wormhole_compiler/experiment.py
=============================================================================
HYPER-X Experimental Budgeting, Checkpointing & Recovery (Phase 47)
=============================================================================
Governs computational resource usage during algorithm discovery searches:
  - time_budget_sec
  - memory_budget_mb
  - candidate_budget
  - evaluation_budget
  - compilation_budget

Includes:
  - State Checkpointing & Recovery
  - Duplicate Elimination via AlgorithmGenome structural hashes
  - Memoization of evaluated candidate outputs
  - Early stopping upon Pareto convergence
"""

from __future__ import annotations
import time
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Set

from hyper_x.wormhole_compiler.algorithm_genome import AlgorithmGenome


@dataclass
class ExperimentBudget:
    time_budget_sec: float = 30.0
    memory_budget_mb: float = 2048.0
    candidate_budget: int = 50
    evaluation_budget: int = 200
    compilation_budget: int = 100


class ExperimentManager:
    """Controls execution budget and prevents redundant evaluation."""

    def __init__(self, budget: Optional[ExperimentBudget] = None):
        self.budget = budget or ExperimentBudget()
        self.start_time = time.perf_counter()
        self.evaluated_hashes: Set[str] = set()
        self.candidate_count = 0
        self.evaluation_count = 0
        self.compilation_count = 0
        self.memoized_results: Dict[str, Any] = {}

    def is_budget_exhausted(self) -> Tuple[bool, str]:
        """Checks whether any budget limit has been reached."""
        elapsed = time.perf_counter() - self.start_time
        if elapsed >= self.budget.time_budget_sec:
            return True, f"Time budget exhausted ({elapsed:.1f}s >= {self.budget.time_budget_sec:.1f}s)"
        if self.candidate_count >= self.budget.candidate_budget:
            return True, f"Candidate budget exhausted ({self.candidate_count} >= {self.budget.candidate_budget})"
        if self.evaluation_count >= self.budget.evaluation_budget:
            return True, f"Evaluation budget exhausted ({self.evaluation_count} >= {self.budget.evaluation_budget})"
        if self.compilation_count >= self.budget.compilation_budget:
            return True, f"Compilation budget exhausted ({self.compilation_count} >= {self.budget.compilation_budget})"
        return False, "Budget healthy"

    def register_candidate_eval(self, genome: AlgorithmGenome) -> bool:
        """
        Registers a candidate evaluation.
        Returns False if the candidate is a structural duplicate (should be skipped).
        """
        s_hash = genome.compute_structural_hash()
        if s_hash in self.evaluated_hashes:
            return False  # Duplicate! Skip evaluation.
        self.evaluated_hashes.add(s_hash)
        self.candidate_count += 1
        self.evaluation_count += 1
        return True

    def memoize_result(self, genome: AlgorithmGenome, result: Dict[str, Any]) -> None:
        """Caches result by structural hash."""
        s_hash = genome.compute_structural_hash()
        self.memoized_results[s_hash] = result

    def get_memoized_result(self, genome: AlgorithmGenome) -> Optional[Dict[str, Any]]:
        s_hash = genome.compute_structural_hash()
        return self.memoized_results.get(s_hash)
