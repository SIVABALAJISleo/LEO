"""
tests/test_hostile_inference.py
===============================
Hostile Self-Falsification Suite: Adversarial Speculative Draft Rejection.

Verifies:
  - An adversarial draft model that produces completely unaligned tokens
    is 100% rejected by target verification without entering an infinite loop.
  - The resulting output sequence remains bitwise-exact identical to target ground truth.
"""

import pytest
import numpy as np
from typing import List
from hyper_cco.workloads.llm_speculative import LlmSpeculativeWorkload, SurrogateLM


class AdversarialDraftLM(SurrogateLM):
    """Hostile draft model that deliberately predicts tokens opposite to target."""
    def forward_step(self, token_ids: List[int]) -> np.ndarray:
        # Predict an arbitrary token (e.g. vocab_size - 1)
        logits = np.zeros(self.vocab_size, dtype=np.float32)
        logits[-1] = 100.0
        return logits


def test_zero_acceptance_adversarial_draft():
    """Adversarial draft with 0% acceptance must safely fall back and match target rollout."""
    wl = LlmSpeculativeWorkload(seed=42)
    # Inject adversarial draft model
    wl.draft_model = AdversarialDraftLM(wl.VOCAB_SIZE, wl.D_MODEL, layers=1, seed=999)

    base = wl.run_baseline()
    cand = wl.run_candidate()

    # Must produce full 32 tokens exactly matching target rollout
    assert cand.shape == (wl.TARGET_TOKENS,)
    assert np.array_equal(cand, base)
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert err_abs == 0.0
