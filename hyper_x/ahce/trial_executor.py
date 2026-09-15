"""
hyper_x/ahce/trial_executor.py
==============================
Controlled Trial Execution Harness for AHCE (Section 11).
"""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .contract import AHCEContract
from .candidate import AHCECandidate, AHCETrialResult
from .evaluator import AHCECandidateEvaluator
from .strategy_registry import AHCEStrategyRegistry


class AHCETrialExecutor:
    """Executes trial candidates sequentially or with early termination on high-confidence exact matches."""

    def __init__(self, registry: AHCEStrategyRegistry):
        self.registry = registry
        self.evaluator = AHCECandidateEvaluator(registry)

    def execute_trials(
        self,
        candidates: List[AHCECandidate],
        A: np.ndarray,
        B: Optional[np.ndarray],
        contract: AHCEContract,
        reference_out: Any,
        reference_latency_ms: float
    ) -> Tuple[AHCETrialResult, List[AHCETrialResult]]:
        trial_results: List[AHCETrialResult] = []
        best_result: Optional[AHCETrialResult] = None

        for cand in candidates:
            res = self.evaluator.evaluate_candidate(
                cand, A, B, contract, reference_out, reference_latency_ms
            )
            trial_results.append(res)

            # Early exit: Exact cache hit verified immediately
            if res.verified and res.strategy_name == "exact_cache" and res.work_reduction_pct >= 99.0:
                best_result = res
                break

            # Track verified candidate with lowest total latency
            if res.verified:
                if best_result is None or res.total_latency_ms < best_result.total_latency_ms:
                    best_result = res

        # If all candidates failed or violated contract, execute safe fallback
        if best_result is None or not best_result.verified:
            fallback_cand = AHCECandidate(
                candidate_id="cand_dense_fallback",
                strategy_name="dense_baseline",
                correctness_class=contract.correctness_class
            )
            best_result = self.evaluator.evaluate_candidate(
                fallback_cand, A, B, contract, reference_out, reference_latency_ms
            )
            best_result.fallback_used = True
            trial_results.append(best_result)

        return best_result, trial_results
