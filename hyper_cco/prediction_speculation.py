"""
hyper_cco/prediction_speculation.py
===================================
Prediction & Speculative Execution Engine.
Executes speculative computation:
Cheap Draft / Prediction -> Confidence Estimation -> Selective Verification -> Accept Prefix / Recompute Rejected Work -> Fallback.
Every predictive result is explicitly classified as PREDICTIVE or SPECULATIVE.
Sampled screening is strictly distinguished from full mathematical verification.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List, Callable
import numpy as np


@dataclass
class SpeculativeResult:
    """Telemetry and outcome of speculative execution."""
    output: Any
    draft_operations: float
    target_verification_operations: float
    fallback_recompute_operations: float
    total_executed_operations: float
    original_operations: float
    work_elimination_ratio: float
    acceptance_rate: float                # Accepted tokens / total tokens or accepted tiles / total tiles
    confidence_score: float
    fallback_triggered: bool
    latency_ms: float
    strategy: str = "SPECULATIVE_EXECUTION"


class SpeculativeEngine:
    """
    Manages speculative drafts, confidence gating, prefix acceptance, and selective fallback.
    """

    @staticmethod
    def execute_speculative_sequence(
        draft_fn: Callable[[], List[int]],
        verify_token_fn: Callable[[int, List[int]], Tuple[bool, int]],
        max_draft_tokens: int = 5,
        target_model_cost_per_token: float = 100.0,
        draft_model_cost_per_token: float = 10.0
    ) -> SpeculativeResult:
        """
        Speculative decoding:
        1. Draft model proposes K tokens.
        2. Target verifier verifies draft tokens in parallel.
        3. Accepts longest valid prefix.
        4. Appends true target token on first divergence.
        """
        t0 = time.perf_counter()
        draft_tokens = draft_fn()[:max_draft_tokens]
        num_draft = len(draft_tokens)

        accepted_tokens: List[int] = []
        rejected = False

        for idx, token in enumerate(draft_tokens):
            context = accepted_tokens.copy()
            is_valid, correct_token = verify_token_fn(token, context)
            if is_valid and not rejected:
                accepted_tokens.append(token)
            else:
                rejected = True
                accepted_tokens.append(correct_token)
                break

        num_accepted = len(accepted_tokens)
        acc_rate = (num_accepted - 1) / max(1, num_draft) if rejected else 1.0

        draft_ops = num_draft * draft_model_cost_per_token
        verify_ops = (num_accepted) * target_model_cost_per_token
        total_ops = draft_ops + verify_ops
        canonical_ops = num_accepted * target_model_cost_per_token

        work_elim = max(0.0, 1.0 - (total_ops / canonical_ops)) if canonical_ops > 0 else 0.0
        latency = (time.perf_counter() - t0) * 1000.0

        return SpeculativeResult(
            output=accepted_tokens,
            draft_operations=draft_ops,
            target_verification_operations=verify_ops,
            fallback_recompute_operations=0.0 if not rejected else target_model_cost_per_token,
            total_executed_operations=total_ops,
            original_operations=canonical_ops,
            work_elimination_ratio=work_elim,
            acceptance_rate=acc_rate,
            confidence_score=acc_rate,
            fallback_triggered=rejected,
            latency_ms=latency,
            strategy="SPECULATIVE_DRAFT_VERIFY"
        )

    @staticmethod
    def execute_speculative_matrix(
        A: np.ndarray,
        B: np.ndarray,
        approximate_matmul_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        error_tolerance: float = 1e-3
    ) -> SpeculativeResult:
        """
        Speculative numerical computation:
        1. Cheap candidate computes Y_approx.
        2. Freivalds-style randomized screening checks ||(Y_approx - A @ B) v||.
        3. If residual exceeds tolerance, recomputes exact fallback.
        """
        t0 = time.perf_counter()
        M, K = A.shape
        K2, N = B.shape
        orig_ops = 2.0 * M * K * N

        # 1. Draft candidate
        Y_approx = approximate_matmul_fn(A, B)
        draft_ops = 0.3 * orig_ops # approximate draft cost

        # 2. Randomized vector screening (O(M*K + K*N) instead of O(M*K*N))
        v = np.random.choice([-1.0, 1.0], size=(N, 1))
        # Check: A @ (B @ v) vs Y_approx @ v
        Bv = B @ v
        ABv = A @ Bv
        Yv = Y_approx @ v
        screen_diff = np.linalg.norm(ABv - Yv)
        norm_ref = np.linalg.norm(ABv)
        rel_diff = screen_diff / max(1e-12, norm_ref)

        screen_ops = 2.0 * K * N + 2.0 * M * K + 2.0 * M * N

        if rel_diff <= error_tolerance:
            # Accepted speculative result
            total_ops = draft_ops + screen_ops
            work_elim = max(0.0, 1.0 - (total_ops / orig_ops)) if orig_ops > 0 else 0.0
            latency = (time.perf_counter() - t0) * 1000.0
            return SpeculativeResult(
                output=Y_approx,
                draft_operations=draft_ops,
                target_verification_operations=screen_ops,
                fallback_recompute_operations=0.0,
                total_executed_operations=total_ops,
                original_operations=orig_ops,
                work_elimination_ratio=work_elim,
                acceptance_rate=1.0,
                confidence_score=1.0 - rel_diff,
                fallback_triggered=False,
                latency_ms=latency,
                strategy="SPECULATIVE_NUMERICAL_ACCEPTED"
            )
        else:
            # Rejected -> fallback to exact BLAS matmul
            output = A @ B
            fallback_ops = orig_ops
            total_ops = draft_ops + screen_ops + fallback_ops
            latency = (time.perf_counter() - t0) * 1000.0
            return SpeculativeResult(
                output=output,
                draft_operations=draft_ops,
                target_verification_operations=screen_ops,
                fallback_recompute_operations=fallback_ops,
                total_executed_operations=total_ops,
                original_operations=orig_ops,
                work_elimination_ratio=0.0,
                acceptance_rate=0.0,
                confidence_score=0.0,
                fallback_triggered=True,
                latency_ms=latency,
                strategy="SPECULATIVE_NUMERICAL_REJECTED_FALLBACK"
            )
