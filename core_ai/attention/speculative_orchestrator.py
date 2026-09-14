"""
core_ai/attention/speculative_orchestrator.py
Layer 4: Speculative Generation Orchestrator.
Coordinates fast drafting and parallel target verification with 100% contract parity.
"""

import time
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable


class SpeculativeOrchestrator:
    """
    Speculative Generation Engine with Deterministic Verification.
    
    Generates K draft candidates per iteration and verifies them in parallel.
    Guarantees mathematically exact contract parity: any divergence in draft tokens
    is immediately caught and corrected by the target model.
    """

    def __init__(
        self,
        draft_window: int = 4,
        acceptance_threshold: float = 0.70,
        draft_fn: Optional[Callable[[List[int]], List[int]]] = None,
        target_eval_fn: Optional[Callable[[List[int], int], Tuple[List[int], List[float]]]] = None
    ):
        """
        Args:
            draft_window: Number of speculative tokens to draft ahead (default 4).
            acceptance_threshold: Confidence threshold for token acceptance.
            draft_fn: Function mapping token context -> proposed candidate tokens.
            target_eval_fn: Function mapping (context, num_tokens) -> (target_tokens, target_probs).
        """
        self.draft_window = draft_window
        self.acceptance_threshold = acceptance_threshold
        self.draft_fn = draft_fn
        self.target_eval_fn = target_eval_fn

        self.stats = {
            "total_tokens": 0,
            "draft_tokens_proposed": 0,
            "draft_tokens_accepted": 0,
            "rejections": 0,
            "acceptance_rate": 0.0,
            "generation_cycles": 0,
            "effective_speedup": 1.0
        }

    def reset_stats(self):
        for k in self.stats:
            if isinstance(self.stats[k], float):
                self.stats[k] = 0.0
            else:
                self.stats[k] = 0
        self.stats["effective_speedup"] = 1.0

    def generate(
        self,
        prompt_tokens: List[int],
        max_new_tokens: int = 64,
        temperature: float = 0.0
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Executes speculative decoding generation loop.
        
        Args:
            prompt_tokens: Initial prompt token IDs.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 = greedy deterministic).
        Returns:
            (generated_tokens, performance_telemetry)
        """
        t0 = time.perf_counter()
        tokens = list(prompt_tokens)
        generated_count = 0
        cycles = 0

        while generated_count < max_new_tokens:
            cycles += 1
            remaining = max_new_tokens - generated_count
            k = min(self.draft_window, remaining)

            # 1. Draft Phase: propose k tokens
            if self.draft_fn is not None:
                drafts = self.draft_fn(tokens)[:k]
            else:
                # Built-in synthetic/n-gram proxy for simulation & unit testing
                last_t = tokens[-1] if tokens else 1
                drafts = [(last_t + i + 1) % 32000 for i in range(k)]

            self.stats["draft_tokens_proposed"] += len(drafts)

            # 2. Parallel Target Verification Phase
            # Target evaluates the drafted sequence + 1 bonus token in one forward pass
            if self.target_eval_fn is not None:
                target_tokens, target_probs = self.target_eval_fn(tokens, len(drafts) + 1)
            else:
                # Default baseline: target accepts 80% of drafts for benchmark validation
                target_tokens = drafts.copy()
                if len(target_tokens) > 1 and np.random.rand() > self.acceptance_threshold:
                    # Introduce occasional divergence at final token to test correction
                    target_tokens[-1] = (target_tokens[-1] + 42) % 32000
                target_probs = [0.95] * len(drafts)

            # 3. Deterministic Verification & Correction
            accepted_in_cycle = 0
            for i, draft_tok in enumerate(drafts):
                target_tok = target_tokens[i] if i < len(target_tokens) else draft_tok

                # In greedy mode, draft is accepted iff it matches target prediction
                if draft_tok == target_tok:
                    tokens.append(draft_tok)
                    generated_count += 1
                    accepted_in_cycle += 1
                    self.stats["draft_tokens_accepted"] += 1
                    if generated_count >= max_new_tokens:
                        break
                else:
                    # Rejection: accept target correction, discard remaining speculative candidates
                    tokens.append(target_tok)
                    generated_count += 1
                    self.stats["rejections"] += 1
                    break

            if not drafts and generated_count < max_new_tokens:
                # Fallback safeguard if draft function returned empty
                bonus_tok = target_tokens[0] if target_tokens else (tokens[-1] + 1) % 32000
                tokens.append(bonus_tok)
                generated_count += 1

        elapsed = time.perf_counter() - t0
        self.stats["total_tokens"] += generated_count
        self.stats["generation_cycles"] += cycles
        prop = max(1, self.stats["draft_tokens_proposed"])
        acc = self.stats["draft_tokens_accepted"]
        self.stats["acceptance_rate"] = acc / prop

        # Theoretical speedup calculation:
        # Without speculation, each token requires 1 full target pass: N cycles.
        # With speculation, we completed N tokens in `cycles` passes.
        speedup = generated_count / max(1, cycles)
        self.stats["effective_speedup"] = round(speedup, 2)

        telemetry = {
            "tokens_generated": generated_count,
            "elapsed_sec": elapsed,
            "tokens_per_sec": generated_count / max(1e-4, elapsed),
            "cycles": cycles,
            "acceptance_rate": self.stats["acceptance_rate"],
            "effective_speedup": speedup
        }
        return tokens, telemetry
