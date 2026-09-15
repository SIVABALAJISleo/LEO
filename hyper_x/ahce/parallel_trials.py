"""
hyper_x/ahce/parallel_trials.py
===============================
Parallel Trial Execution for AHCE (Section 11).

Evaluates candidate pathways concurrently across CPU cores where beneficial,
incorporating all trial synchronization and evaluation overhead into the total cost.
"""

from __future__ import annotations
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .contract import AHCEContract
from .candidate import AHCECandidate, AHCETrialResult
from .evaluator import AHCECandidateEvaluator
from .strategy_registry import AHCEStrategyRegistry


class AHCEParallelTrialExecutor:
    """Executes candidate evaluations concurrently using host thread pools."""

    def __init__(self, registry: AHCEStrategyRegistry, max_workers: int = 4):
        self.registry = registry
        self.max_workers = max_workers
        self.evaluator = AHCECandidateEvaluator(registry)

    def execute_parallel_trials(
        self,
        candidates: List[AHCECandidate],
        A: np.ndarray,
        B: Optional[np.ndarray],
        contract: AHCEContract,
        reference_out: Any,
        reference_latency_ms: float
    ) -> Tuple[AHCETrialResult, List[AHCETrialResult], float]:
        t_wall_start = time.perf_counter_ns()
        results: List[AHCETrialResult] = []

        # If only 1 candidate, avoid thread pool overhead
        if len(candidates) <= 1:
            cand = candidates[0] if candidates else AHCECandidate("fallback", "dense_baseline", contract.correctness_class)
            res = self.evaluator.evaluate_candidate(cand, A, B, contract, reference_out, reference_latency_ms)
            results.append(res)
            wall_ms = (time.perf_counter_ns() - t_wall_start) / 1e6
            return res, results, wall_ms

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(candidates))) as executor:
            future_map = {
                executor.submit(
                    self.evaluator.evaluate_candidate,
                    cand, A, B, contract, reference_out, reference_latency_ms
                ): cand
                for cand in candidates
            }

            for fut in as_completed(future_map):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:
                    cand = future_map[fut]
                    results.append(AHCETrialResult(
                        candidate_id=cand.candidate_id,
                        strategy_name=cand.strategy_name,
                        success=False,
                        verified=False,
                        output=reference_out,
                        trial_latency_ms=0.0,
                        transformation_latency_ms=0.0,
                        execution_latency_ms=0.0,
                        verification_latency_ms=0.0,
                        total_latency_ms=0.0,
                        measured_error=1.0,
                        necessary_work_units=0.0,
                        work_reduction_pct=0.0,
                        fallback_used=True,
                        details=f"Thread failed: {str(e)}"
                    ))

        wall_ms = (time.perf_counter_ns() - t_wall_start) / 1e6

        # Select fastest verified candidate
        verified_candidates = [r for r in results if r.verified]
        if verified_candidates:
            best_result = min(verified_candidates, key=lambda r: r.total_latency_ms)
        else:
            # Fallback
            best_result = self.evaluator.evaluate_candidate(
                AHCECandidate("fallback", "dense_baseline", contract.correctness_class),
                A, B, contract, reference_out, reference_latency_ms
            )
            best_result.fallback_used = True
            results.append(best_result)

        return best_result, results, wall_ms
