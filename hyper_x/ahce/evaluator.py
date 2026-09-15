"""
hyper_x/ahce/evaluator.py
=========================
Candidate pathway evaluator for AHCE.
"""

from __future__ import annotations
import time
from typing import Dict, Any, Tuple, Optional
import numpy as np

from .contract import AHCEContract
from .candidate import AHCECandidate, AHCETrialResult
from .strategy_registry import AHCEStrategyRegistry, AHCEStrategy
from .verifier import AHCEVerifier
from .cost_model import AHCECostModel


class AHCECandidateEvaluator:
    """Evaluates a single candidate against the contract and independent reference."""

    def __init__(self, registry: AHCEStrategyRegistry):
        self.registry = registry
        self.verifier = AHCEVerifier()
        self.cost_model = AHCECostModel()

    def evaluate_candidate(
        self,
        candidate: AHCECandidate,
        A: np.ndarray,
        B: Optional[np.ndarray],
        contract: AHCEContract,
        reference_out: Any,
        reference_latency_ms: float
    ) -> AHCETrialResult:
        strat = self.registry.get(candidate.strategy_name)
        if strat is None:
            return AHCETrialResult(
                candidate_id=candidate.candidate_id,
                strategy_name=candidate.strategy_name,
                success=False,
                verified=False,
                output=reference_out,
                trial_latency_ms=reference_latency_ms,
                transformation_latency_ms=0.0,
                execution_latency_ms=reference_latency_ms,
                verification_latency_ms=0.0,
                total_latency_ms=reference_latency_ms,
                measured_error=0.0,
                necessary_work_units=0.0,
                work_reduction_pct=0.0,
                fallback_used=True,
                details=f"Strategy '{candidate.strategy_name}' not found."
            )

        # 1. Execute strategy
        t0 = time.perf_counter_ns()
        try:
            cand_out, telem = strat.execute(A, B, contract)
            exec_time_ms = (time.perf_counter_ns() - t0) / 1e6
            success = True
        except Exception as e:
            exec_time_ms = (time.perf_counter_ns() - t0) / 1e6
            return AHCETrialResult(
                candidate_id=candidate.candidate_id,
                strategy_name=candidate.strategy_name,
                success=False,
                verified=False,
                output=reference_out,
                trial_latency_ms=exec_time_ms,
                transformation_latency_ms=0.0,
                execution_latency_ms=exec_time_ms,
                verification_latency_ms=0.0,
                total_latency_ms=exec_time_ms,
                measured_error=1.0,
                necessary_work_units=0.0,
                work_reduction_pct=0.0,
                fallback_used=True,
                details=f"Execution raised error: {str(e)}"
            )

        # 2. Independent Verification
        t_ver_start = time.perf_counter_ns()
        verdict = self.verifier.verify(cand_out, reference_out, contract, A=A, B=B)
        verif_time_ms = (time.perf_counter_ns() - t_ver_start) / 1e6

        # 3. Cost Accounting (Transformation + Execution + Verification)
        trans_time_ms = telem.get("factorization_cost_ms", telem.get("thresholding_cost_ms", 0.0))
        total_time_ms = trans_time_ms + exec_time_ms + verif_time_ms

        dims = A.shape
        M = dims[0] if len(dims) > 0 else 1
        K = dims[1] if len(dims) > 1 else 1
        ref_ops = float(2 * M * K * K)

        if candidate.strategy_name == "exact_cache" and telem.get("cache_hit"):
            cand_ops = 0.0
        elif candidate.strategy_name == "low_rank_svd":
            r = telem.get("rank", 16)
            cand_ops = float(2 * M * r * K)
        elif candidate.strategy_name == "sparse_csr":
            density = telem.get("density", 1.0)
            cand_ops = float(ref_ops * density)
        else:
            cand_ops = ref_ops

        work_red = max(0.0, (1.0 - (cand_ops / max(1.0, ref_ops))) * 100.0)

        return AHCETrialResult(
            candidate_id=candidate.candidate_id,
            strategy_name=candidate.strategy_name,
            success=success,
            verified=verdict.passed,
            output=cand_out if verdict.passed else reference_out,
            trial_latency_ms=round(exec_time_ms, 3),
            transformation_latency_ms=round(trans_time_ms, 3),
            execution_latency_ms=round(exec_time_ms, 3),
            verification_latency_ms=round(verif_time_ms, 3),
            total_latency_ms=round(total_time_ms, 3),
            measured_error=round(verdict.max_rel_error, 6),
            necessary_work_units=cand_ops,
            work_reduction_pct=round(work_red, 2),
            fallback_used=not verdict.passed,
            details=verdict.details
        )
