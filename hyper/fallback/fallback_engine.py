"""
hyper/fallback/fallback_engine.py
=================================
Adaptive Fallback Engine:
Executes cascading progressive fallback:
CHEAPEST -> MEDIUM -> EXPENSIVE -> EXACT_FALLBACK
Guarantees valid mathematical output is returned even under severe domain corruption.
"""

from typing import Dict, Any, List, Callable, Optional, Tuple


class AdaptiveFallbackEngine:
    """
    Manages safe multi-tiered fallback cascades.
    """
    def __init__(self):
        self.fallback_history: List[Dict[str, Any]] = []

    def execute_cascade(
        self,
        workload_name: str,
        tiers: List[Tuple[str, Callable[[], Tuple[Any, bool, float]]]], # (tier_name, fn) -> (result, verified, error)
        exact_fallback_fn: Callable[[], Any]
    ) -> Tuple[Any, str, float]:
        """
        Attempts each tier sequentially. Falls back to exact computation if all fail.
        """
        for tier_name, fn in tiers:
            try:
                result, verified, error = fn()
                if verified:
                    self.fallback_history.append({
                        "workload_name": workload_name,
                        "tier_accepted": tier_name,
                        "status": "ACCEPTED",
                        "error": error
                    })
                    return result, tier_name, error
            except Exception:
                continue

        # Terminal exact fallback
        exact_res = exact_fallback_fn()
        self.fallback_history.append({
            "workload_name": workload_name,
            "tier_accepted": "EXACT_FALLBACK",
            "status": "FALLBACK_ACCEPTED",
            "error": 0.0
        })
        return exact_res, "EXACT_FALLBACK", 0.0
