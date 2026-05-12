"""
backend/analytics/metrics.py
Real Metrics Tracking System (No hardcoded/simulated numbers)
"""
import logging
import time
import os
import json

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

    def log_request(self, request_id: str, query: str, path_taken: str, latency_ms: float, model_called: bool, is_prediction_hit: bool = False, is_recovery: bool = False, canonical: str = ""):
        """
        Point 17: REAL METRICS ENGINE.
        Logs to metrics.jsonl. Avoidance = 1 - (model_calls / total).
        """
        log_entry = {
            "req_id": request_id,
            "query": query,
            "canonical": canonical,
            "path": path_taken,
            "latency": float(f"{latency_ms:.2f}"),
            "model_call": model_called,
            "pred_hit": is_prediction_hit,
            "ts": float(f"{time.time():.4f}")
        }
        
        try:
            with open("metrics.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception: pass

    def get_metrics(self) -> dict:
        """Point 18: Benchmark Validation."""
        reqs, calls, cache_hits = 0, 0, 0
        lats = []
        
        if os.path.exists("metrics.jsonl"):
            with open("metrics.jsonl", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    d = json.loads(line)
                    reqs += 1
                    if d.get("model_call"): calls += 1
                    if "memory" in d.get("path", "") or "prediction" in d.get("path", "") or "reuse" in d.get("path", ""):
                        cache_hits += 1
                    lats.append(d.get("latency", 0))
        
        avoidance = (1.0 - (calls / reqs)) * 100 if reqs > 0 else 0.0
        avg_lat = sum(lats) / len(lats) if lats else 0.0
        
        return {
            "total_requests": reqs,
            "model_calls": calls,
            "cache_hits": cache_hits,
            "avoidance_rate": f"{avoidance:.2f}%",
            "avg_latency_ms": f"{avg_lat:.2f}ms"
        }

global_metrics = AnalyticsSystem()