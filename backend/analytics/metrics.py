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

    def log_request(self, request_id: str, query: str, path_taken: str, latency_ms: float, model_called: bool, is_prediction_hit: bool = False, is_recovery: bool = False):
        """
        Point 9: Real metrics logging to metrics.jsonl.
        Tracks Model Avoidance and Recovery Efficiency.
        """
        log_entry = {
            "req_id": request_id,
            "path": path_taken,
            "latency": float(f"{latency_ms:.2f}"),
            "model_call": model_called,
            "pred_hit": is_prediction_hit,
            "recovered": is_recovery,
            "ts": float(f"{time.time():.4f}")
        }
        
        try:
            with open("metrics.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"metrics: log write failed: {e}")

    def get_metrics(self) -> dict:
        """
        Point 9: Verification Engine - 98% Avoidance Target Tracker.
        """
        reqs, calls, pred_hits, recovered = 0, 0, 0, 0
        lats = []
        
        if os.path.exists("metrics.jsonl"):
            try:
                with open("metrics.jsonl", "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip(): continue
                        d = json.loads(line)
                        reqs += 1
                        if d.get("model_call"): calls += 1
                        if d.get("pred_hit"): pred_hits += 1
                        if d.get("recovered"): recovered += 1
                        lats.append(d.get("latency", 0))
            except Exception as e:
                logger.error(f"metrics: log read error: {e}")
        
        avoidance = 1.0 - (calls / reqs) if reqs > 0 else 0.0
        prediction_hit_rate = pred_hits / reqs if reqs > 0 else 0.0
        recovery_rate = recovered / reqs if reqs > 0 else 0.0
        avg_lat = sum(lats) / len(lats) if lats else 0.0
        
        return {
            "total_requests": reqs,
            "model_calls": calls,
            "avoidance_rate": float(f"{avoidance:.4f}"),
            "prediction_hit_rate": float(f"{prediction_hit_rate:.4f}"),
            "failure_recovery_rate": float(f"{recovery_rate:.4f}"),
            "avg_latency_ms": float(f"{avg_lat:.2f}"),
            "reuse_rate": float(f"{(reqs - calls) / reqs:.4f}") if reqs > 0 else 0.0
        }

global_metrics = AnalyticsSystem()