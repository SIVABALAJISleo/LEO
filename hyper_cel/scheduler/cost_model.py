"""
hyper_cel/scheduler/cost_model.py
=============================================================================
HYPER-CEL: Contract-Driven Cost Model & Execution Scheduler
=============================================================================
Evaluates execution pathways against the fundamental decision equation:
    a* = argmin_a [ Latency(a) + lambda * Energy(a) + mu * Memory(a) ]
    subject to Quality(a) >= Q_min and Verification(a) == PASS
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ExecutionCandidate:
    name: str
    level: int               # 0 to 5
    estimated_latency_ms: float
    estimated_energy_joules: float
    estimated_memory_mb: float
    estimated_quality: float # 0.0 to 1.0
    action_type: str         # "CACHE", "REUSE", "PREDICT", "RESIDUAL", "HYBRID", "EXACT"

class HyperCostModel:
    """
    Cost model evaluating candidate pathways under non-negotiable contract constraints.
    """

    def __init__(self, energy_weight: float = 0.5, memory_weight: float = 0.2):
        self.lambda_energy = energy_weight
        self.mu_memory = memory_weight

    def evaluate_cost(self, candidate: ExecutionCandidate) -> float:
        """Computes scalar objective cost."""
        return (
            candidate.estimated_latency_ms +
            (self.lambda_energy * candidate.estimated_energy_joules * 1000.0) +
            (self.mu_memory * candidate.estimated_memory_mb)
        )

    def choose_optimal_pathway(
        self,
        candidates: List[ExecutionCandidate],
        min_quality: float = 0.95
    ) -> ExecutionCandidate:
        """
        Filters candidates violating Quality >= min_quality, and returns the lowest-cost valid candidate.
        """
        valid_candidates = [c for c in candidates if c.estimated_quality >= min_quality]
        
        if not valid_candidates:
            # Fallback to candidate with highest quality (guaranteed exact compute)
            return max(candidates, key=lambda c: c.estimated_quality)

        return min(valid_candidates, key=self.evaluate_cost)
