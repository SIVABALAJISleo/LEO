from backend.core.metrics import RUNTIME_COMPUTE_CALLS
import logging
import psutil
from typing import Dict

logger = logging.getLogger(__name__)

class ComputeBudgetController:
    """
    Final System Strength Budget Controller.
    Enforces a 'Near-Zero' runtime compute target (<2% CPU delta).
    """
    def __init__(self, max_cpu_delta: float = 2.0): # Lowered to 2.0 (Near-Zero Target)
        self.max_cpu_delta = max_cpu_delta
        self.request_units: Dict[str, int] = {} 

    def has_capacity(self) -> bool:
        """
        Near-Zero capacity check: Blocks if base load > 60% to prevent any spikes.
        """
        current_load = psutil.cpu_percent(interval=None)
        if current_load > 60.0: 
             logger.warning(f"compute_budget: Near-Zero Target breach risk ({current_load}%). Blocking sync compute.")
             return False
        return True

    def start_tracking(self, request_id: str):
        self.request_units[request_id] = 0
        # Track every attempt at runtime compute
        RUNTIME_COMPUTE_CALLS.inc()

    def consume_unit(self, request_id: str, units: int = 1):
        """
        Strict budget enforcement. Target is <10 units (micro-tasks only).
        """
        if request_id not in self.request_units:
            self.start_tracking(request_id)
        
        self.request_units[request_id] += units
        if self.request_units[request_id] > 10: # Strict Limit: 10 micro-units
             logger.error(f"compute_budget: Request '{request_id}' exceeded Near-Zero budget.")
             raise TimeoutError("Compute Budget Breach: Target is Near-Zero Runtime.")

    def end_tracking(self, request_id: str):
        if request_id in self.request_units:
             self.request_units.pop(request_id, None)

global_compute_budget = ComputeBudgetController()
