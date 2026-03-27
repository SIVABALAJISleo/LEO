"""
backend/optimization/heat_scheduler.py
Heat-Aware Scheduler for Zero Runtime Compute.

Monitors CPU usage and switches to lightweight mode if load is too high (> 70%).
"""
import psutil
import logging

logger = logging.getLogger(__name__)

class HeatAwareScheduler:
    def __init__(self, cpu_threshold: float = 70.0):
        self.cpu_threshold = cpu_threshold
        self.is_overheated = False

    def check_load(self) -> bool:
        """
        Returns True if CPU usage is below threshold.
        Returns False if CPU usage exceeds threshold (overheated).
        """
        cpu_usage = psutil.cpu_percent(interval=None)
        if cpu_usage > self.cpu_threshold:
            if not self.is_overheated:
                logger.warning(f"heat_scheduler: CPU threshold breached ({cpu_usage}%). Switching to LIGHTWEIGHT mode.")
                self.is_overheated = True
            return False
        
        if self.is_overheated:
            logger.info(f"heat_scheduler: CPU load normalized ({cpu_usage}%). Returning to NORMAL mode.")
            self.is_overheated = False
        return True

    def should_skip_heavy_logic(self) -> bool:
        """Helper to determine if expensive runtime logic should be skipped."""
        return not self.check_load()

global_heat_scheduler = HeatAwareScheduler()
