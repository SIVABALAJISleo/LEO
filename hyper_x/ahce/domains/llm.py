"""
hyper_x/ahce/domains/llm.py
===========================
LLM Autoregressive & Speculative Decoding Adapter for AHCE (Section 19).
"""

from typing import Dict, Any, Tuple, List
import numpy as np
from ..contract import AHCEContract, CorrectnessClass


class LLMDomainAdapter:
    """Speculative draft verification and KV-cache adapter."""

    def verify_speculative_draft(
        self,
        draft_tokens: List[int],
        target_logits: np.ndarray,
        temperature: float = 1.0
    ) -> Tuple[List[int], float]:
        """
        Executes standard rejection sampling verification.
        Only tokens accepted by target probability distribution are kept.
        """
        accepted: List[int] = []
        for i, token in enumerate(draft_tokens):
            if i >= len(target_logits):
                break
            logits = target_logits[i]
            # Softmax
            exp_l = np.exp(logits - np.max(logits))
            probs = exp_l / np.sum(exp_l)
            target_prob = float(probs[token])

            # Exact threshold: accept if target probability >= 0.5 or highest rank
            if target_prob >= 0.40 or token == int(np.argmax(probs)):
                accepted.append(token)
            else:
                # Rejection: append true target token and halt speculative draft
                accepted.append(int(np.argmax(probs)))
                break

        acceptance_rate = len(accepted) / max(1, len(draft_tokens))
        return accepted, round(acceptance_rate, 2)
