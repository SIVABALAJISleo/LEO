import time
from typing import Tuple

class AntiHaltingService:
    """
    20. BOUNDED REASONING (ANTI-HALTING)
    """
    def __init__(self, time_limit_ms: int = 5000, depth_limit: int = 10):
        self.time_limit_ms = time_limit_ms
        self.depth_limit = depth_limit
        self.start_time = 0

    def start_track(self):
        self.start_time = time.time() * 1000

    def check_limits(self, current_depth: int) -> Tuple[bool, str]:
        elapsed = (time.time() * 1000) - self.start_time
        if elapsed > self.time_limit_ms:
            return False, f"TIME_LIMIT_EXCEEDED: {elapsed:.2f}ms"
        if current_depth > self.depth_limit:
            return False, f"DEPTH_LIMIT_EXCEEDED: {current_depth} steps"
        return True, "SAFE"

