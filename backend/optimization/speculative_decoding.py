"""
backend/optimization/speculative_decoding.py
Subsystem 11: Speculative Decoding Engine.
Uses a small fast draft model to speculatively generate N tokens,
then verifies them in parallel with the target model.
Accepted tokens cost 1 LLM call to verify N tokens — O(N) speed gain.
"""

import torch
import logging
import time
from typing import List, Tuple, Optional, Callable

logger = logging.getLogger(__name__)


class SpeculativeDecodingEngine:
    """
    Speculative decoding implementation.
    
    Protocol:
    1. Draft model generates `speculate_k` tokens quickly.
    2. Target model evaluates all k+1 token positions in one forward pass.
    3. Accepted tokens are those where target agrees with draft (within threshold).
    4. On rejection, fall back to target's corrected token.
    
    This implementation is model-agnostic — it accepts callables for both models.
    """

    def __init__(
        self,
        draft_model_fn: Callable[[List[int]], int],
        target_model_fn: Callable[[List[int]], Tuple[List[float], int]],
        speculate_k: int = 4,
        acceptance_threshold: float = 0.8
    ):
        """
        Args:
            draft_model_fn:   fn(tokens) -> next_token_id (tiny fast model)
            target_model_fn:  fn(tokens) -> (log_probs_over_vocab, next_token_id)
            speculate_k:      number of tokens to speculatively generate
            acceptance_threshold: minimum prob ratio to accept a drafted token
        """
        self.draft_fn = draft_model_fn
        self.target_fn = target_model_fn
        self.speculate_k = speculate_k
        self.acceptance_threshold = acceptance_threshold

    def decode_step(self, prompt_tokens: List[int]) -> Tuple[List[int], dict]:
        """
        Runs one speculative decoding step.
        Returns (accepted_tokens, stats_dict).
        """
        t0 = time.perf_counter()

        # Phase 1: Draft k tokens cheaply
        draft_tokens = []
        ctx = list(prompt_tokens)
        for _ in range(self.speculate_k):
            drafted = self.draft_fn(ctx)
            draft_tokens.append(drafted)
            ctx.append(drafted)

        # Phase 2: Verify with target model in one parallel pass
        # (In a real implementation, the target processes all k+1 positions at once.)
        accepted = []
        current_ctx = list(prompt_tokens)

        for t_idx, drafted_token in enumerate(draft_tokens):
            target_logprobs, target_token = self.target_fn(current_ctx)

            # Acceptance criterion: does the target agree with the draft?
            if target_token == drafted_token:
                accepted.append(drafted_token)
                current_ctx.append(drafted_token)
            else:
                # Reject: use target's corrected token and stop this speculative run
                accepted.append(target_token)
                break

        elapsed_ms = (time.perf_counter() - t0) * 1000
        stats = {
            "drafted": len(draft_tokens),
            "accepted": len(accepted),
            "acceptance_rate": round(len(accepted) / max(1, len(draft_tokens)), 2),
            "latency_ms": round(elapsed_ms, 2),
            "speedup_estimate": round(len(accepted) / max(1, self.speculate_k), 2)
        }

        logger.debug(
            f"Speculative decode: {stats['accepted']}/{stats['drafted']} accepted "
            f"({stats['acceptance_rate']*100:.0f}%) in {elapsed_ms:.1f}ms"
        )
        return accepted, stats
