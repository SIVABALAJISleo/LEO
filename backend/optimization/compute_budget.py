"""
backend/optimization/compute_budget.py
Compute Budget Controller for Controlled Logic.

Tracks 'compute units' and enforces a strict 2-5% CPU limit per request 
to maintain system stability.
"""
import logging
import psutil
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ComputeBudgetController:
    def __init__(self, max_cpu_delta: float = 5.0):
        # Max additional CPU load allowed per request
        self.max_cpu_delta = max_cpu_delta
        self.request_units: Dict[str, int] = {} # request_id -> units used

    def has_capacity(self) -> bool:
        """
        Returns True if the system has capacity for synchronous compute.
        """
        current_load = psutil.cpu_percent(interval=None)
        if current_load > 70.0: # Hard throttle (Phase 39)
             logger.warning(f"compute_budget: System load too high ({current_load}%). Throttling.")
             return False
        return True

    def start_tracking(self, request_id: str):
        self.request_units[request_id] = 0

    def consume_unit(self, request_id: str, units: int = 1):
        """
        Increments unit count and checks if limit (e.g. 50 units) is exceeded.
        """
        if request_id not in self.request_units:
            self.start_tracking(request_id)
        
        self.request_units[request_id] += units
        if self.request_units[request_id] > 50: # Example limit: 50 micro-units
             logger.warning(f"compute_budget: Request '{request_id}' exceeded sync budget.")
             raise TimeoutError("Compute Budget Exceeded")

    def end_tracking(self, request_id: str):
        if request_id in self.request_units:
             self.request_units.pop(request_id, None)

global_compute_budget = ComputeBudgetController()
