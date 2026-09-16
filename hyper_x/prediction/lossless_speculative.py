"""
hyper_x/prediction/lossless_speculative.py
==========================================
Phase 13: Lossless Speculative Execution Engine.
Pipeline:
  Draft -> Candidate Sequence -> Target Verification -> Accept Verified Prefix -> Reject Invalid Suffix -> Continue
Rule:
  A prediction is NEVER equivalent merely because it looks plausible.
  Lossless mode requires exact agreement with the target reference distribution.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class SpeculativeStepResult:
    accepted_tokens: List[int]
    rejected_tokens: List[int]
    accepted_count: int
    draft_count: int
    acceptance_rate: float
    verification_latency_ms: float
    is_lossless: bool


class LosslessSpeculativeEngine:
    """
    Guarantees mathematically exact autoregressive generation via target distribution verification.
    """

    @staticmethod
    def verify_and_accept(
        draft_tokens: List[int],
        target_verifier_fn: Callable[[List[int]], List[int]],
        prefix_context: List[int],
    ) -> SpeculativeStepResult:
        """
        Verifies draft tokens sequentially against target verifier model.
        Accepts the exact matching prefix; immediately rejects the remainder upon divergence.
        """
        t0 = time.perf_counter()
        accepted: List[int] = []
        rejected: List[int] = []

        current_ctx = list(prefix_context)
        # Target generates the true reference sequence for this step
        true_targets = target_verifier_fn(current_ctx + draft_tokens)

        # Step-by-step exact verification
        for idx, draft_tok in enumerate(draft_tokens):
            if idx < len(true_targets) and draft_tok == true_targets[idx]:
                accepted.append(draft_tok)
            else:
                # Discrepancy detected: reject this token and all subsequent suffix tokens
                rejected = draft_tokens[idx:]
                break

        t_ms = (time.perf_counter() - t0) * 1000.0
        acc_rate = len(accepted) / max(1, len(draft_tokens))

        return SpeculativeStepResult(
            accepted_tokens=accepted,
            rejected_tokens=rejected,
            accepted_count=len(accepted),
            draft_count=len(draft_tokens),
            acceptance_rate=round(acc_rate, 4),
            verification_latency_ms=round(t_ms, 3),
            is_lossless=True,  # Because every accepted token matched the target exactly
        )
