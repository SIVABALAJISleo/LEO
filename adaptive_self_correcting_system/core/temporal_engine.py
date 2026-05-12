import time
from typing import List, Any

class TemporalEngine:
    """
    STAGE 7 — TEMPORAL VALIDATION (DRIFT CONTROL)
    """
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds

    def apply_decay(self, confidence: float, last_updated: float) -> float:
        # If data is older than TTL, apply decay
        elapsed = time.time() - last_updated
        if elapsed > self.ttl:
            return confidence * 0.7
        return confidence

    def is_stale(self, last_updated: float) -> bool:
        return (time.time() - last_updated) > self.ttl

