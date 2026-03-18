"""
Latency-Aware Engine
Monitors system load and automatically skips expensive pipeline layers
when latency budget is exceeded or system load is high.
"""
import time
import logging
import psutil
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Latency budgets per complexity tier (ms)
LATENCY_BUDGETS = {
    "low":    100,   # Simple queries: max 100ms
    "medium": 500,   # Medium: max 500ms
    "high":   2000,  # Complex: max 2 seconds
}

# Layers skipped when system is overloaded
SKIP_WHEN_HIGH_LOAD = ["micro_model", "large_model"]
SKIP_WHEN_CRITICAL_LOAD = ["enhancement", "micro_model", "large_model"]

CPU_HIGH_THRESHOLD = 80.0     # % CPU usage
CPU_CRITICAL_THRESHOLD = 95.0


class LatencyController:
    """
    Adapts pipeline execution to real-time system load.
    When load is high, expensive layers are skipped to preserve latency SLOs.
    """

    def __init__(self):
        self._start_times: Dict[str, float] = {}

    def start_timer(self, request_id: str):
        self._start_times[request_id] = time.time()

    def elapsed_ms(self, request_id: str) -> float:
        t = self._start_times.get(request_id)
        if t is None:
            return 0.0
        return (time.time() - t) * 1000

    def get_cpu_load(self) -> float:
        try:
            return psutil.cpu_percent(interval=None)
        except Exception:
            return 0.0

    def is_overloaded(self) -> bool:
        return self.get_cpu_load() >= CPU_HIGH_THRESHOLD

    def is_critically_loaded(self) -> bool:
        return self.get_cpu_load() >= CPU_CRITICAL_THRESHOLD

    def filter_plan(self, plan: List[str], complexity: str = "medium") -> List[str]:
        """
        Removes expensive layers from plan based on current system load.
        """
        cpu = self.get_cpu_load()

        if cpu >= CPU_CRITICAL_THRESHOLD:
            filtered = [l for l in plan if l not in SKIP_WHEN_CRITICAL_LOAD]
            logger.warning(f"latency_critical_load: cpu={cpu:.0f}% skipping={SKIP_WHEN_CRITICAL_LOAD}")
            return filtered

        if cpu >= CPU_HIGH_THRESHOLD:
            filtered = [l for l in plan if l not in SKIP_WHEN_HIGH_LOAD]
            logger.info(f"latency_high_load: cpu={cpu:.0f}% skipping={SKIP_WHEN_HIGH_LOAD}")
            return filtered

        return plan

    def should_abort_layer(self, request_id: str, complexity: str) -> bool:
        """Returns True if we've exceeded latency budget and should skip remaining layers."""
        elapsed = self.elapsed_ms(request_id)
        budget = LATENCY_BUDGETS.get(complexity, 500)
        if elapsed > budget * 0.85:
            logger.info(f"latency_budget_near: elapsed={elapsed:.0f}ms budget={budget}ms")
            return True
        return False

    def stats(self) -> Dict[str, Any]:
        return {
            "current_cpu_pct": self.get_cpu_load(),
            "overloaded": self.is_overloaded(),
        }


global_latency_controller = LatencyController()
