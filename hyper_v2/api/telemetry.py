"""
hyper_v2/api/telemetry.py
Telemetry collector for tracking verified work avoidance and fallback rates.
"""

from typing import Dict, Any, List
import time


class TelemetryTracker:
    """Records execution metrics, work avoidance statistics, and fallback invocations."""

    _events: List[Dict[str, Any]] = []

    @classmethod
    def record_execution(cls, workload_id: str, track: str, time_ms: float, work_avoided_pct: float, verified: bool, level: int):
        cls._events.append({
            "timestamp": time.time(),
            "workload_id": workload_id,
            "track": track,
            "time_ms": time_ms,
            "work_avoided_pct": work_avoided_pct,
            "verified": verified,
            "fallback_level": level
        })

    @classmethod
    def get_aggregate_stats(cls) -> Dict[str, Any]:
        if not cls._events:
            return {
                "total_executions": 0,
                "average_work_avoided_pct": 0.0,
                "verification_pass_rate_pct": 100.0,
                "fallback_rate_pct": 0.0
            }

        total = len(cls._events)
        avg_avoided = sum(e["work_avoided_pct"] for e in cls._events) / total
        passes = sum(1 for e in cls._events if e["verified"])
        fallbacks = sum(1 for e in cls._events if e["fallback_level"] == 8)

        return {
            "total_executions": total,
            "average_work_avoided_pct": round(avg_avoided, 2),
            "verification_pass_rate_pct": round((passes / total) * 100.0, 2),
            "fallback_rate_pct": round((fallbacks / total) * 100.0, 2)
        }
