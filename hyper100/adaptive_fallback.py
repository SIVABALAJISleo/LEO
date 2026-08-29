"""
hyper100/adaptive_fallback.py
=============================
Adaptive Fallback & Escalation Engine.
Guarantees zero contract violation by escalating execution fidelity
(increasing precision, rank, or density) whenever an optimization candidate fails verification.
"""

import time
from typing import Dict, Any, Tuple, Optional, Callable, List
from dataclasses import dataclass, field
import numpy as np

from .contract_engine import ExecutionContract, VerificationStatus
from .verification_engine import VerificationEngine, VerificationReport


@dataclass
class FallbackTrace:
    """Audit record of escalation path taken during execution."""
    attempts: int
    strategies_attempted: List[str]
    final_strategy: str
    fallback_triggered: bool
    final_verification: VerificationReport
    total_elapsed_ms: float


class AdaptiveFallbackEngine:
    """Executes candidate optimizations with guaranteed contract-safe fallbacks."""

    @classmethod
    def execute_with_fallback(
        cls,
        candidate_fns: List[Tuple[str, Callable[[], Any]]],
        exact_baseline_fn: Callable[[], Any],
        contract: ExecutionContract,
        invariants_fn: Optional[Callable[[Any], Tuple[bool, float]]] = None
    ) -> Tuple[Any, FallbackTrace]:
        """
        Tries candidate optimization functions in order of lowest estimated cost.
        If verification fails, escalates to next fidelity or exact baseline.
        """
        t0 = time.perf_counter()
        strategies_tried: List[str] = []
        baseline_cached: Optional[Any] = None

        for name, fn in candidate_fns:
            strategies_tried.append(name)
            try:
                candidate_out = fn()
                # If exactness contract requires comparison against baseline
                if contract.is_exact_required() or contract.exactness in ("BOUNDED_ERROR", "NUMERICALLY_EQUIVALENT", ContractExactness.BOUNDED_ERROR, ContractExactness.NUMERICALLY_EQUIVALENT):
                    if baseline_cached is None:
                        baseline_cached = exact_baseline_fn()
                    v_report = VerificationEngine.verify(candidate_out, baseline_cached, contract, invariants_fn)
                else:
                    v_report = VerificationEngine.verify(candidate_out, None, contract, invariants_fn)

                if v_report.is_valid:
                    total_ms = (time.perf_counter() - t0) * 1000.0
                    trace = FallbackTrace(
                        attempts=len(strategies_tried),
                        strategies_attempted=strategies_tried,
                        final_strategy=name,
                        fallback_triggered=(len(strategies_tried) > 1),
                        final_verification=v_report,
                        total_elapsed_ms=total_ms
                    )
                    return candidate_out, trace

            except Exception:
                # Any runtime exception triggers immediate escalation to next candidate
                pass

        # Final guarantee: execute exact baseline
        strategies_tried.append("EXACT_BASELINE_FALLBACK")
        if baseline_cached is None:
            baseline_cached = exact_baseline_fn()

        v_report = VerificationEngine.verify(baseline_cached, baseline_cached, contract, invariants_fn)
        total_ms = (time.perf_counter() - t0) * 1000.0

        trace = FallbackTrace(
            attempts=len(strategies_tried),
            strategies_attempted=strategies_tried,
            final_strategy="EXACT_BASELINE_FALLBACK",
            fallback_triggered=True,
            final_verification=v_report,
            total_elapsed_ms=total_ms
        )
        return baseline_cached, trace
