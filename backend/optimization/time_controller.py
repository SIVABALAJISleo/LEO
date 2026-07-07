"""
backend/optimization/time_controller.py
Time Budget Controller for Zero Runtime Compute.

Enforces a strict 50ms processing limit for runtime requests.
"""
import time
import logging

logger = logging.getLogger(__name__)

class TimeBudgetController:
    def __init__(self, budget_ms: float = 50.0):
        self.budget_ms = budget_ms
        self.start_times: dict = {}

    def start(self, request_id: str):
        """Starts tracking time for a request."""
        self.start_times[request_id] = time.perf_counter()

    def check(self, request_id: str) -> bool:
        """
        Returns True if the budget is still within limits.
        Returns False if the budget is exceeded.
        """
        if request_id not in self.start_times:
            return True
            
        elapsed = (time.perf_counter() - self.start_times[request_id]) * 1000
        if elapsed > self.budget_ms:
            logger.warning(f"time_controller: Budget exceeded for '{request_id}' ({elapsed:.2f}ms > {self.budget_ms}ms)")
            return False
        return True

    def elapsed(self, request_id: str) -> float:
        """Returns elapsed time in ms."""
        if request_id not in self.start_times:
            return 0.0
        return (time.perf_counter() - self.start_times[request_id]) * 1000

    def cleanup(self, request_id: str):
        """Cleans up request state."""
        if request_id in self.start_times:
            del self.start_times[request_id]

global_time_controller = TimeBudgetController()
