"""
LEO AI V42 - The Irrelevance Engine
Phase 2: The Infinite Cache Layer (99.9% Compute Avoidance)

Real-time dashboard metrics and analytics for the 5-tier cache hierarchy.
Provides observability into compute avoidance efficiency.
"""

from collections import defaultdict
from typing import Dict, Any

class CacheAnalytics:
    def __init__(self):
        self.hits_by_tier = defaultdict(int)
        self.latency_by_tier = defaultdict(list)
        self.miss_reasons = defaultdict(int)
        
        self.total_requests = 0
        self.total_flops_saved = 0.0

    def record_hit(self, tier_name: str, latency_ms: float):
        self.total_requests += 1
        self.hits_by_tier[tier_name] += 1
        self.latency_by_tier[tier_name].append(latency_ms)
        
        # Estimate flops saved (assuming 70B model processing 100 tokens = ~14 TeraFLOPs)
        self.total_flops_saved += 14.0

    def record_miss(self, latency_ms: float, reason: str = "novel_query"):
        self.total_requests += 1
        self.miss_reasons[reason] += 1

    def get_metrics(self) -> Dict[str, Any]:
        hit_count = sum(self.hits_by_tier.values())
        hit_rate = (hit_count / self.total_requests) if self.total_requests > 0 else 0.0
        
        avg_latencies = {}
        for tier, lats in self.latency_by_tier.items():
            if lats:
                # Keep last 100 for moving average
                if len(lats) > 100:
                    lats = lats[-100:]
                    self.latency_by_tier[tier] = lats
                avg_latencies[tier] = sum(lats) / len(lats)

        return {
            "total_requests": self.total_requests,
            "overall_hit_rate": hit_rate,
            "hits_by_tier": dict(self.hits_by_tier),
            "average_latency_ms": avg_latencies,
            "miss_reasons_distribution": dict(self.miss_reasons),
            "estimated_tflops_saved": self.total_flops_saved
        }

global_cache_metrics = CacheAnalytics()
