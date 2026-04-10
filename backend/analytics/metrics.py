"""
backend/analytics/metrics.py
Real Metrics Tracking System (No hardcoded/simulated numbers)
"""
import logging

logger = logging.getLogger(__name__)

class AnalyticsSystem:
    def __init__(self):
        self._queries = 0
        self._model_calls = 0
        self._shadow_hits = 0
        self._cache_hits = 0
        self._rag_hits = 0
        self._delta_hits = 0
        self._micro_model_hits = 0
        
        # Zero Runtime Compute Metrics
        self._runtime_compute_calls = 0 # Target: 0
        self._background_compute_tasks = 0
        self._predictive_hit_rate = 0.0
        self._reuse_rate = 0.0

        # Unknown Handling Metrics (used by get_metrics)
        self._unknown_query_count = 0
        self._unknown_handled_without_model = 0
        self._composition_successes = 0
        self._micro_compute_usage = 0

        # Final Optimization Metrics (99% Efficiency)
        self._soft_match_hits = 0
        self._early_exits = 0
        self._approximation_count = 0
        self._latencies = []

    def track_query(self):
        self._queries += 1

    def track_model_call(self, is_runtime: bool = True):
        self._model_calls += 1
        if is_runtime:
            self._runtime_compute_calls += 1
        else:
            self._background_compute_tasks += 1

    def track_hit(self, hit_type: str):
        if hit_type == "shadow":
            self._shadow_hits += 1
        elif hit_type == "cache":
            self._cache_hits += 1
        elif hit_type == "rag":
            self._rag_hits += 1
        elif hit_type == "delta":
            self._delta_hits += 1
        elif hit_type == "micro":
            self._micro_model_hits += 1
        elif hit_type == "soft_match":
            self._soft_match_hits += 1
        elif hit_type == "early_exit":
            self._early_exits += 1
        elif hit_type == "approx":
            self._approximation_count += 1
            
    def track_latency(self, latency_ms: float):
        self._latencies.append(latency_ms)
        if len(self._latencies) > 1000:
            self._latencies.pop(0)

    def track_unknown_event(self, event_type: str):
        if event_type == "query":
            self._unknown_query_count += 1
        elif event_type == "handled_without_model":
            self._unknown_handled_without_model += 1
        elif event_type == "composition_success":
            self._composition_successes += 1
        elif event_type == "micro_compute":
            self._micro_compute_usage += 1

    def get_metrics(self) -> dict:
        avoidance = 1.0 if self._queries == 0 else 1.0 - (self._runtime_compute_calls / max(1, self._queries))
        avg_lat = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
        
        return {
            "total_queries": self._queries,
            "runtime_compute_calls": self._runtime_compute_calls,
            "avg_latency_ms": float(f"{avg_lat:.2f}"),
            "avoidance_rate": float(f"{avoidance:.4f}"),
            "optimization_stats": {
                "soft_match_hits": self._soft_match_hits,
                "early_exits": self._early_exits,
                "approx_answers": self._approximation_count,
            }
        }

global_metrics = AnalyticsSystem()