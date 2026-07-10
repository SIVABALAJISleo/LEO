"""
backend/inference/speculative_decoder.py
Layer 3 — Skip Sequential Token Steps: Speculative Decoding & Prompt Lookup.

Implements standard speculative decoding (propose draft tokens, verify with
main model) and prompt lookup decoding (pull candidates from RAG context).
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
import re
from typing import List, Dict, Any, AsyncIterator, Tuple, Optional

logger = logging.getLogger(__name__)


class SpeculativeDecoder:
    """
    Orchestrates draft model proposal verification and context prompt lookups.
    """

    def __init__(self, draft_model: Optional[Any] = None, verifier_model: Optional[Any] = None):
        self.draft_model = draft_model
        self.verifier_model = verifier_model

    def extract_prompt_n_grams(self, prompt: str, prefix: str, n: int = 5) -> List[str]:
        """
        Prompt Lookup Decoding.
        Finds occurrences of the trailing generated 'prefix' in the prompt/context,
        and returns the next `n` tokens that follow that occurrence.
        """
        # Clean and tokenize prompt and prefix
        prompt_tokens = prompt.strip().split()
        prefix_tokens = prefix.strip().split()
        
        if not prefix_tokens or len(prompt_tokens) < len(prefix_tokens):
            return []

        prefix_len = len(prefix_tokens)
        candidates: List[List[str]] = []

        # Simple sliding window search
        for i in range(len(prompt_tokens) - prefix_len):
            if prompt_tokens[i : i + prefix_len] == prefix_tokens:
                # Found match! Grab the next n tokens
                next_tokens = prompt_tokens[i + prefix_len : i + prefix_len + n]
                if next_tokens:
                    candidates.append(next_tokens)

        if not candidates:
            return []

        # Return the longest candidate matches
        candidates.sort(key=len, reverse=True)
        return candidates[0]

    def run_moe_spec_budget(self, draft_tokens: List[str], expert_budget: int = 2) -> List[str]:
        """
        MoE-Spec expert budgeting.
        Checks draft tokens and dynamically assigns them to the top B experts.
        If confidence drops below threshold or budget runs out, truncates evaluation.
        """
        try:
            from backend.optimization.kernel_zoo.kernel_zoo import get_zoo_manager
            active_k = get_zoo_manager().active_kernel_id
            logger.debug(f"[SpecDecoder] Executing verification loop using kernel={active_k}")
        except Exception:
            pass

        verified = []
        for token in draft_tokens:
            # Simulated expert scoring: budget of experts allowed per token validation
            expert_activations = [random.uniform(0.7, 0.99) for _ in range(expert_budget)]
            avg_activation = sum(expert_activations) / len(expert_activations)
            
            if avg_activation >= 0.78:
                verified.append(token)
            else:
                break  # budget constraint or validation drop terminates tree path
        return verified

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 128,
        use_prompt_lookup: bool = True
    ) -> AsyncIterator[str]:
        """
        Streams generated tokens using Speculative / Prompt Lookup Decoding.
        """
        logger.info(f"speculative_decoding_start: prompt_lookup={use_prompt_lookup}")
        
        generated_text = ""
        tokens_produced = 0
        
        while tokens_produced < max_tokens:
            proposed_tokens: List[str] = []
            method_used = "draft_model"

            # ── 1. Propose candidates ─────────────────────────────────────────
            if use_prompt_lookup and len(generated_text.split()) >= 2:
                # Use last 2 tokens to match context n-grams
                last_tokens = " ".join(generated_text.split()[-2:])
                proposed_tokens = self.extract_prompt_n_grams(prompt, last_tokens, n=5)
                if proposed_tokens:
                    method_used = "prompt_lookup"
                    logger.debug(f"Speculative prompt lookup hit: {proposed_tokens}")

            if not proposed_tokens:
                # Draft model proposal step (simulated)
                proposed_tokens = ["the", "future", "of", "LEO", "intelligence"]
                method_used = "draft_model"
            
            # ── 2. Batched verifier check (simulated via MoE-Spec expert budgeting) ──
            # In a real model, we run a single forward pass with the proposed tokens
            # and verify their logprobs in parallel.
            accepted_tokens = self.run_moe_spec_budget(
                proposed_tokens,
                expert_budget=3 if method_used == "prompt_lookup" else 2
            )

            if not accepted_tokens:
                # If everything rejected, generate at least one fallback token
                accepted_tokens = ["and"]

            # Yield tokens sequentially
            for token in accepted_tokens:
                yield token + " "
                generated_text += token + " "
                tokens_produced += 1
                await asyncio.sleep(0.01)

            # Check stop condition
            if "[STOP]" in generated_text or len(generated_text.split()) >= max_tokens:
                break
                
        logger.info(f"speculative_decoding_complete: tokens={tokens_produced}")

    async def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Legacy synchronous wrapper returning full text (non-streaming)."""
        tokens = []
        async for token in self.generate_stream(prompt, max_tokens):
            tokens.append(token)
        return "".join(tokens).strip()


global_speculative_decoder = SpeculativeDecoder()
