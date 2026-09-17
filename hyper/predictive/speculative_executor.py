"""
Speculative Execution & Residual Computation for LEO/HYPER Ω.
Implements: Draft -> Verify -> Commit / Rollback / Fallback.

Enforces strict economic profitability:
If (draft_cost + verify_cost + (1 - hit_rate) * fallback_cost) >= exact_cost,
speculation is dynamically disabled.
"""

import time
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Tuple, Dict
import numpy as np

from contracts.contract_ir import ContractIR, Contract100Gate


@dataclass
class SpeculationStats:
    total_attempts: int = 0
    successful_commits: int = 0
    rollbacks: int = 0
    avg_draft_time_ms: float = 0.0
    avg_verify_time_ms: float = 0.0
    avg_fallback_time_ms: float = 0.0
    speculation_enabled: bool = True
    disabled_reason: Optional[str] = None


class SpeculativeExecutor:
    """
    Executes operations speculatively using a fast draft generator,
    verifying correctness against the contract before committing.
    """

    def __init__(self, warmup_runs: int = 5, min_profitability_threshold: float = 1.05):
        self.stats = SpeculationStats()
        self.warmup_runs = warmup_runs
        self.min_profitability_threshold = min_profitability_threshold
        self._history = []

    def execute(
        self,
        draft_fn: Callable[[], np.ndarray],
        verify_fn: Optional[Callable[[np.ndarray], bool]],
        exact_fallback_fn: Callable[[], np.ndarray],
        contract: ContractIR,
        op_name: str = "speculative_op"
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes speculatively if profitable, else falls back directly to exact.
        """
        self.stats.total_attempts += 1

        # Check if speculation is currently disabled
        if not self.stats.speculation_enabled:
            t0 = time.perf_counter()
            exact_res = exact_fallback_fn()
            t1 = time.perf_counter()
            fallback_ms = (t1 - t0) * 1000.0
            return exact_res, {
                "speculation_used": False,
                "reason": self.stats.disabled_reason or "disabled",
                "latency_ms": fallback_ms,
                "committed": False
            }

        # Step 1: Draft
        t_d0 = time.perf_counter()
        try:
            draft_res = draft_fn()
        except Exception as e:
            draft_res = None
        t_d1 = time.perf_counter()
        draft_ms = (t_d1 - t_d0) * 1000.0

        # Step 2: Verify
        t_v0 = time.perf_counter()
        passed_contract = False
        if draft_res is not None:
            if verify_fn is not None:
                passed_contract = verify_fn(draft_res)
            else:
                # Default verification: run exact and check tolerance
                # (Used during profiling/warmup or lightweight residual checking)
                t_exact_0 = time.perf_counter()
                exact_check = exact_fallback_fn()
                t_exact_1 = time.perf_counter()
                ref_ms = (t_exact_1 - t_exact_0) * 1000.0

                gate = Contract100Gate.validate(
                    reference_output=exact_check,
                    hyper_output=draft_res,
                    contract=contract,
                    ref_latency_ms=ref_ms,
                    hyper_latency_ms=draft_ms,
                    peak_ram_bytes=draft_res.nbytes,
                    work_eliminated_ratio=0.5
                )
                passed_contract = gate.passed
                if passed_contract:
                    self.stats.successful_commits += 1
                    t_v1 = time.perf_counter()
                    verify_ms = (t_v1 - t_v0) * 1000.0
                    self._update_stats(draft_ms, verify_ms, ref_ms, success=True)
                    return draft_res, {
                        "speculation_used": True,
                        "committed": True,
                        "draft_latency_ms": draft_ms,
                        "verify_latency_ms": verify_ms,
                        "total_latency_ms": draft_ms + verify_ms
                    }
                else:
                    self.stats.rollbacks += 1
                    t_v1 = time.perf_counter()
                    verify_ms = (t_v1 - t_v0) * 1000.0
                    self._update_stats(draft_ms, verify_ms, ref_ms, success=False)
                    return exact_check, {
                        "speculation_used": True,
                        "committed": False,
                        "rollback_reason": "Contract validation failed",
                        "draft_latency_ms": draft_ms,
                        "verify_latency_ms": verify_ms,
                        "total_latency_ms": draft_ms + verify_ms + ref_ms
                    }

        t_v1 = time.perf_counter()
        verify_ms = (t_v1 - t_v0) * 1000.0

        # Step 3: Rollback & Execute Exact Fallback
        if not passed_contract:
            self.stats.rollbacks += 1
            t_f0 = time.perf_counter()
            exact_res = exact_fallback_fn()
            t_f1 = time.perf_counter()
            fallback_ms = (t_f1 - t_f0) * 1000.0

            self._update_stats(draft_ms, verify_ms, fallback_ms, success=False)

            return exact_res, {
                "speculation_used": True,
                "committed": False,
                "draft_latency_ms": draft_ms,
                "verify_latency_ms": verify_ms,
                "fallback_latency_ms": fallback_ms,
                "total_latency_ms": draft_ms + verify_ms + fallback_ms
            }

        # Step 4: Commit
        self.stats.successful_commits += 1
        self._update_stats(draft_ms, verify_ms, 0.0, success=True)
        return draft_res, {
            "speculation_used": True,
            "committed": True,
            "draft_latency_ms": draft_ms,
            "verify_latency_ms": verify_ms,
            "total_latency_ms": draft_ms + verify_ms
        }

    def _update_stats(self, draft_ms: float, verify_ms: float, fallback_ms: float, success: bool):
        self._history.append((draft_ms, verify_ms, fallback_ms, success))
        if len(self._history) > 50:
            self._history.pop(0)

        # Recompute averages
        n = len(self._history)
        self.stats.avg_draft_time_ms = sum(h[0] for h in self._history) / n
        self.stats.avg_verify_time_ms = sum(h[1] for h in self._history) / n
        non_zero_fb = [h[2] for h in self._history if h[2] > 0]
        self.stats.avg_fallback_time_ms = sum(non_zero_fb) / max(1, len(non_zero_fb))

        # Check economic profitability
        if n >= self.warmup_runs:
            hit_rate = self.stats.successful_commits / max(1, self.stats.total_attempts)
            expected_spec_cost = (
                self.stats.avg_draft_time_ms +
                self.stats.avg_verify_time_ms +
                (1.0 - hit_rate) * self.stats.avg_fallback_time_ms
            )
            # Compare to fallback (exact cost)
            if self.stats.avg_fallback_time_ms > 0:
                cost_ratio = expected_spec_cost / self.stats.avg_fallback_time_ms
                if cost_ratio >= self.min_profitability_threshold:
                    self.stats.speculation_enabled = False
                    self.stats.disabled_reason = (
                        f"Speculation unprofitable: expected cost {expected_spec_cost:.2f}ms >= "
                        f"exact cost {self.stats.avg_fallback_time_ms:.2f}ms (ratio {cost_ratio:.2f}x)"
                    )
