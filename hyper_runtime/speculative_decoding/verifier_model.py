import time
import numpy as np
from typing import List, Tuple

class VerifierModel:
    """
    Primary Heavy compute model.
    Evaluates draft tokens in parallel (using a single forward pass) to verify them.
    If a token is rejected, generation falls back to this model for correction.
    """
    def __init__(self, vocab_size: int = 10000, latency_ms: float = 40.0):
        self.vocab_size = vocab_size
        self.latency_ms = latency_ms / 1000.0
        
    def verify_and_correct(self, context: List[int], draft_tokens: List[int], acceptance_rate: float = 0.7) -> Tuple[List[int], int]:
        """
        Simulates parallel verification of k draft tokens.
        Returns: (accepted_tokens + corrected_token, number_of_accepted_drafts)
        """
        # The cost of verifying K tokens in parallel is roughly equivalent to generating 1 token
        time.sleep(self.latency_ms)
        
        accepted = []
        np.random.seed(sum(context) + sum(draft_tokens))
        
        for token in draft_tokens:
            # Simulate acceptance based on the target acceptance rate
            if np.random.rand() < acceptance_rate:
                accepted.append(token)
            else:
                break # Sequence breaks on first rejection
                
        # If rejected, the verifier model corrects the sequence by generating the true next token
        corrected_token = np.random.randint(0, self.vocab_size)
        
        return accepted + [corrected_token], len(accepted)
        
    def generate_single(self, context: List[int]) -> int:
        """Standard autoregressive generation."""
        time.sleep(self.latency_ms)
        return np.random.randint(0, self.vocab_size)
