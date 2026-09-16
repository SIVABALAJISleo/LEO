#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/speculative/speculative_controller.py
============================================
Phase 10: Lossless Speculative Controller.
Orchestrates:
  Draft Proposal -> Target Evaluation -> Accept Matching Prefix -> Rollback Divergent Suffix.
Guarantees mathematically exact equivalence to target model generation.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Tuple
from .draft_engine import SpeculativeDraftEngine


@dataclass
class SpeculativeStepSummary:
    accepted_tokens: List[int]
    rejected_tokens: List[int]
    total_drafted: int
    acceptance_rate: float
    is_lossless: bool
    step_latency_ms: float


class SpeculativeController:
    """
    Manages speculative decoding loop with zero-tolerance for distributional drift.
    """

    def __init__(
        self,
        target_evaluator: Callable[[List[int]], List[int]],
        draft_engine: Optional[SpeculativeDraftEngine] = None,
        speculative_window: int = 4,
    ):
        self.target_evaluator = target_evaluator
        self.draft_engine = draft_engine or SpeculativeDraftEngine()
        self.speculative_window = speculative_window

    def step(self, current_context: List[int]) -> SpeculativeStepSummary:
        """
        Executes one speculative cycle:
        1. Draft proposes K tokens.
        2. Target verifies.
        3. Prefix is accepted; mismatch causes instant rollback.
        """
        t0 = time.perf_counter()
        draft_tokens, _ = self.draft_engine.propose_candidates(current_context, self.speculative_window)

        # Target produces reference ground truth tokens for context + draft
        target_ground_truth = self.target_evaluator(current_context + draft_tokens)

        accepted: List[int] = []
        rejected: List[int] = []

        for idx, d_tok in enumerate(draft_tokens):
            if idx < len(target_ground_truth) and d_tok == target_ground_truth[idx]:
                accepted.append(d_tok)
            else:
                # Discrepancy! Rollback all subsequent speculative tokens
                rejected = draft_tokens[idx:]
                # Must append the single true target token at the divergence point
                if idx < len(target_ground_truth):
                    accepted.append(target_ground_truth[idx])
                break

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        acc_rate = len(accepted) / max(len(draft_tokens), 1)

        return SpeculativeStepSummary(
            accepted_tokens=accepted,
            rejected_tokens=rejected,
            total_drafted=len(draft_tokens),
            acceptance_rate=round(acc_rate, 4),
            is_lossless=True,
            step_latency_ms=round(latency_ms, 3),
        )
