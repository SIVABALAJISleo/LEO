import time
import numpy as np
from typing import List

class DraftModel:
    """
    Lightweight CPU-friendly draft model.
    Generates speculative tokens extremely fast but with lower accuracy.
    """
    def __init__(self, vocab_size: int = 10000, latency_ms: float = 2.0):
        self.vocab_size = vocab_size
        self.latency_ms = latency_ms / 1000.0

    def generate_draft(self, context: List[int], k_tokens: int) -> List[int]:
        """
        Generates k draft tokens sequentially.
        """
        # Simulate sequential generation latency
        time.sleep(self.latency_ms * k_tokens)
        
        # Mock token generation
        np.random.seed(sum(context) % (2**32))
        draft_tokens = np.random.randint(0, self.vocab_size, size=k_tokens).tolist()
        return draft_tokens
