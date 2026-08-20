"""
core_ai/dynamic_cache_profiler.py
The HYPER Protocol v2.0: Dynamic Cache Profiling Window
Eliminates assumed static cache hit rates (e.g. 'assumed 80%').
Maintains a rolling 1,000-query profiling window to measure empirical hit rate and
effective latency dynamically on live user workloads.
"""

import time
from collections import deque
from typing import Dict, Any, Optional, List

class CacheQueryEvent:
    def __init__(self, query: str, cache_hit: bool, latency_ms: float):
        self.query = query
        self.cache_hit = cache_hit
        self.latency_ms = latency_ms
        self.timestamp = time.time()

class DynamicCacheProfiler:
    """
    Dynamic Cache Profiler tracking rolling empirical statistics.
    """
    def __init__(self, window_size: int = 1000, min_samples_for_claim: int = 50):
        self.window_size = window_size
        self.min_samples = min_samples_for_claim
        self.history: deque = deque(maxlen=window_size)
        
    def record_query(self, query: str, cache_hit: bool, latency_ms: float):
        """Records a live query execution event."""
        self.history.append(CacheQueryEvent(query, cache_hit, latency_ms))
        
    def get_effective_metrics(self) -> Dict[str, Any]:
        """
        Calculates dynamic empirical hit rate and effective latency.
        """
        total_queries = len(self.history)
        if total_queries < self.min_samples:
            return {
                "status": "COLLECTING_DATA",
                "sample_count": total_queries,
                "min_required_samples": self.min_samples,
                "claim_valid": False,
                "message": f"Insufficient query history ({total_queries}/{self.min_samples}) to claim statistical parity."
            }
            
        hits = sum(1 for q in self.history if q.cache_hit)
        measured_hit_rate = hits / total_queries
        
        hit_latencies = [q.latency_ms for q in self.history if q.cache_hit]
        miss_latencies = [q.latency_ms for q in self.history if not q.cache_hit]
        
        avg_hit_ms = sum(hit_latencies) / len(hit_latencies) if hit_latencies else 0.06
        avg_miss_ms = sum(miss_latencies) / len(miss_latencies) if miss_latencies else 26.76
        
        effective_latency_ms = (measured_hit_rate * avg_hit_ms) + ((1.0 - measured_hit_rate) * avg_miss_ms)
        
        return {
            "status": "STATISTICALLY_VALID",
            "sample_count": total_queries,
            "window_size": self.window_size,
            "measured_hit_rate": measured_hit_rate,
            "measured_hit_rate_percentage": measured_hit_rate * 100.0,
            "avg_cache_hit_latency_ms": avg_hit_ms,
            "avg_active_inference_latency_ms": avg_miss_ms,
            "effective_dynamic_latency_ms": effective_latency_ms,
            "baseline_gpu_latency_ms": 15.0, # RTX 3060 active generation
            "speedup_vs_gpu": 15.0 / max(1e-4, effective_latency_ms),
            "claim_valid": True,
            "scientific_claim": f"Under live workload (N={total_queries}), HYPER measured a {measured_hit_rate * 100.0:.1f}% hit rate, yielding a dynamic effective latency of {effective_latency_ms:.2f} ms."
        }
