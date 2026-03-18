"""
Cost-Aware Controller
Estimates compute cost per query and forces lower-cost execution paths
when cost thresholds are exceeded.
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Estimated cost per layer (USD per 1000 requests)
LAYER_COSTS = {
    "canonical":      0.00001,
    "template":       0.00001,
    "graph":          0.00005,
    "reasoning_mem":  0.00005,
    "semantic_cache": 0.00010,
    "retrieval":      0.00100,
    "enhancement":    0.00050,
    "micro_model":    0.00500,
    "large_model":    0.05000,  # 500x more expensive than canonical
}

# Daily cost budget (USD) — forces cheaper paths when approaching limit
DAILY_BUDGET_USD = 10.0


class CostController:
    """
    Tracks estimated cost per query and per session.
    Forces lower-compute paths when thresholds are exceeded.
    """

    def __init__(self):
        self._day_start = time.time()
        self._day_total = 0.0
        self._request_costs: Dict[str, float] = {}

    def _reset_if_new_day(self):
        if time.time() - self._day_start > 86400:
            self._day_start = time.time()
            self._day_total = 0.0
            logger.info("cost_controller_daily_reset")

    def estimate_cost(self, layer: str) -> float:
        """Estimate cost for executing a given pipeline layer."""
        return LAYER_COSTS.get(layer, 0.001)

    def record(self, layer: str, request_id: str):
        """Record actual cost incurred for a request."""
        self._reset_if_new_day()
        cost = self.estimate_cost(layer)
        self._day_total += cost
        self._request_costs[request_id] = self._request_costs.get(request_id, 0) + cost
        logger.debug(f"cost_recorded: layer={layer} request={request_id} day_total=${self._day_total:.4f}")

    def should_force_cheap_path(self, complexity: str = "medium") -> bool:
        """
        Returns True if the system should force lower-cost execution.
        Triggered when approaching daily budget or for low-priority requests.
        """
        self._reset_if_new_day()
        budget_ratio = self._day_total / DAILY_BUDGET_USD

        if budget_ratio > 0.90:
            logger.warning(f"cost_budget_critical: {budget_ratio:.0%} used")
            return True
        if budget_ratio > 0.75 and complexity == "low":
            return True
        return False

    def force_skip_layers(self, current_plan: list) -> list:
        """Remove expensive layers from plan under budget pressure."""
        skip = {"large_model", "micro_model"} if self._day_total / DAILY_BUDGET_USD > 0.90 else {"large_model"}
        return [l for l in current_plan if l not in skip]

    def daily_stats(self) -> Dict[str, Any]:
        self._reset_if_new_day()
        return {
            "day_total_usd": round(self._day_total, 4),
            "budget_usd": DAILY_BUDGET_USD,
            "budget_used_pct": round(self._day_total / DAILY_BUDGET_USD * 100, 1),
        }


global_cost_controller = CostController()
