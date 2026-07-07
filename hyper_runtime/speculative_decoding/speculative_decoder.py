import logging
import time
from typing import Dict, Any

from .draft_model import DraftModel
from .verifier_model import VerifierModel
from .replay_assisted_speculation import ReplayAssistedSpeculator

logger = logging.getLogger("HyperCore.SpeculativeDecoder")

class SpeculativeExecutionEngine:
    """
    HyperCore MODULE 5 — Speculative Execution Engine
    
    Accelerates autoregressive generation by guessing tokens with a small draft model
    (or semantic cache) and verifying them in parallel with a large model.
    """
    def __init__(self, k_draft_tokens: int = 4, acceptance_rate: float = 0.7):
        self.k_draft = k_draft_tokens
        self.acceptance_rate = acceptance_rate
        
        self.draft_model = DraftModel(latency_ms=2.0)
        self.verifier_model = VerifierModel(latency_ms=40.0) # 20x slower
        self.replay_speculator = ReplayAssistedSpeculator()
        
        logger.info(f"SpeculativeExecutionEngine initialized with k={self.k_draft}, gamma={self.acceptance_rate}")

    def generate(self, prompt: str, target_length: int = 20) -> Dict[str, Any]:
        """
        Generates sequence using speculative decoding.
        """
        t_start = time.perf_counter()
        
        context_tokens = [1, 2, 3] # Mock initial prompt tokens
        generated_tokens = []
        
        metrics = {
            "total_draft_tokens": 0,
            "accepted_draft_tokens": 0,
            "draft_model_calls": 0,
            "verifier_calls": 0,
            "replay_assisted_drafts": 0,
            "wall_clock_time": 0.0,
            "baseline_time_estimate": 0.0
        }
        
        while len(generated_tokens) < target_length:
            # 1. Try Replay-Assisted Draft
            draft_tokens = self.replay_speculator.get_draft_from_cache(prompt, self.k_draft, offset=len(generated_tokens))
            
            if draft_tokens:
                metrics["replay_assisted_drafts"] += len(draft_tokens)
            else:
                # 2. Fallback to Draft Model
                draft_tokens = self.draft_model.generate_draft(context_tokens + generated_tokens, self.k_draft)
                metrics["draft_model_calls"] += 1
                
            metrics["total_draft_tokens"] += len(draft_tokens)
            
            # 3. Parallel Verification
            # Verifier checks all draft tokens at once + generates 1 correct token if rejected
            valid_seq, num_accepted = self.verifier_model.verify_and_correct(
                context_tokens + generated_tokens, 
                draft_tokens, 
                acceptance_rate=self.acceptance_rate
            )
            
            metrics["verifier_calls"] += 1
            metrics["accepted_draft_tokens"] += num_accepted
            
            generated_tokens.extend(valid_seq)
            
            # We generated `len(valid_seq)` tokens this step (num_accepted + 1)
            # which might overshoot target_length slightly.
            if len(generated_tokens) >= target_length:
                generated_tokens = generated_tokens[:target_length]
                break

        metrics["wall_clock_time"] = time.perf_counter() - t_start
        # Baseline time = generating target_length tokens sequentially with the verifier
        metrics["baseline_time_estimate"] = target_length * self.verifier_model.latency_ms
        
        speedup = metrics["baseline_time_estimate"] / metrics["wall_clock_time"]
        acceptance_ratio = metrics["accepted_draft_tokens"] / max(1, metrics["total_draft_tokens"])
        
        metrics["speedup_factor"] = round(speedup, 2)
        metrics["acceptance_ratio"] = round(acceptance_ratio, 3)
        
        return {
            "tokens": generated_tokens,
            "metrics": metrics
        }
