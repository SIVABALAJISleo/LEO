"""
hyper_v3/telemetry/tracker.py
Real-time telemetry collector tracking execution latencies, work avoidance, and fallback events.
"""

from typing import Dict, Any, List
import time


class TelemetryTracker:
    """Records runtime telemetry and aggregate system performance."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.fallback_count: int = 0
        self.total_executions: int = 0

    def record_execution(self, workload_name: str, latency_us: float, vwa: float, fell_back: bool = False):
        self.total_executions += 1
        if fell_back:
            self.fallback_count += 1
        self.events.append({
            "workload": workload_name,
            "latency_us": latency_us,
            "vwa": vwa,
            "fallback": fell_back,
            "timestamp": time.time()
        })

    def get_summary(self) -> Dict[str, Any]:
        fallback_rate = (self.fallback_count / self.total_executions) if self.total_executions > 0 else 0.0
        return {
            "total_executions": self.total_executions,
            "fallback_count": self.fallback_count,
            "fallback_rate": fallback_rate,
            "recent_events_count": len(self.events)
        }
