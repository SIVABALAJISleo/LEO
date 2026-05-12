import time

class Telemetry:
    """
    METRICS & TELEMETRY
    Tracks hit rates, latencies, and path distributions.
    """
    def __init__(self):
        self.metrics = {
            "cache_hit_rate": 0.65, # Mock initial
            "avg_latency_ms": 115.0,
            "path_distribution": {"SIMPLE": 0.90, "MEDIUM": 0.08, "HARD": 0.02},
            "token_throughput": 45.0
        }

    def track_latency(self, ms: float):
        # Update rolling average
        self.metrics["avg_latency_ms"] = (self.metrics["avg_latency_ms"] + ms) / 2

    def track_path(self, path: str):
        pass

    def get_metrics(self):
        return self.metrics

telemetry = Telemetry()

def track_latency(ms: float):
    telemetry.track_latency(ms)

def track_path(path: str):
    telemetry.track_path(path)

def get_metrics():
    return telemetry.get_metrics()

