"""
Metrics collection and reporting for the entire IRA system.
Tracks every measurable aspect of every pillar.
"""
import time
import threading
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from collections import deque

@dataclass
class PillarMetrics:
    """Metrics for a single pillar."""
    pillar_name: str
    total_calls: int = 0
    total_hits: int = 0
    total_misses: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    recent_latencies: deque = field(
        default_factory=lambda: deque(maxlen=1000)
    )
    extra_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def hit_rate(self) -> float:
        return self.total_hits / max(1, self.total_calls)

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / max(1, self.total_calls)

    @property
    def p50_latency_ms(self) -> float:
        if not self.recent_latencies:
            return 0.0
        sorted_lat = sorted(self.recent_latencies)
        return sorted_lat[len(sorted_lat) // 2]

    @property
    def p95_latency_ms(self) -> float:
        if not self.recent_latencies:
            return 0.0
        sorted_lat = sorted(self.recent_latencies)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    @property
    def p99_latency_ms(self) -> float:
        if not self.recent_latencies:
            return 0.0
        sorted_lat = sorted(self.recent_latencies)
        idx = int(len(sorted_lat) * 0.99)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    def record_call(self, is_hit: bool, latency_ms: float,
                    is_error: bool = False, **kwargs):
        self.total_calls += 1
        if is_hit:
            self.total_hits += 1
        else:
            self.total_misses += 1
        if is_error:
            self.total_errors += 1
        self.total_latency_ms += latency_ms
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)
        self.recent_latencies.append(latency_ms)
        for k, v in kwargs.items():
            self.extra_metrics[k] = v

    def to_dict(self) -> dict:
        return {
            "pillar_name": self.pillar_name,
            "total_calls": self.total_calls,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_errors": self.total_errors,
            "hit_rate": round(self.hit_rate, 6),
            "avg_latency_ms": round(self.avg_latency_ms, 6),
            "min_latency_ms": round(self.min_latency_ms, 6) if self.min_latency_ms != float('inf') else 0,
            "max_latency_ms": round(self.max_latency_ms, 6),
            "p50_latency_ms": round(self.p50_latency_ms, 6),
            "p95_latency_ms": round(self.p95_latency_ms, 6),
            "p99_latency_ms": round(self.p99_latency_ms, 6),
            "extra_metrics": self.extra_metrics
        }

@dataclass
class SystemMetrics:
    """Top-level metrics for the entire IRA system."""
    start_time: float = field(default_factory=time.time)
    total_queries_processed: int = 0
    total_response_time_ms: float = 0.0
    effective_tokens_per_second: float = 0.0
    pillars: Dict[str, PillarMetrics] = field(default_factory=dict)
    compute_breakdown: Dict[str, float] = field(default_factory=dict)

    def get_or_create_pillar(self, name: str) -> PillarMetrics:
        if name not in self.pillars:
            self.pillars[name] = PillarMetrics(pillar_name=name)
        return self.pillars[name]

    def to_dict(self) -> dict:
        uptime_seconds = time.time() - self.start_time
        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "total_queries_processed": self.total_queries_processed,
            "avg_response_time_ms": round(
                self.total_response_time_ms / max(1, self.total_queries_processed), 6
            ),
            "effective_tokens_per_second": round(
                self.effective_tokens_per_second, 2
            ),
            "queries_per_second": round(
                self.total_queries_processed / max(0.1, uptime_seconds), 4
            ),
            "pillars": {
                name: pm.to_dict() for name, pm in self.pillars.items()
            },
            "compute_breakdown": self.compute_breakdown
        }

class MetricCollector:
    """
    Thread-safe metrics collector for the entire IRA system.
    Single global instance accessed by all pillars.
    """
    _instance: Optional['MetricCollector'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.system = SystemMetrics()
        self._export_lock = threading.Lock()
        self._initialized = True

    def record_query(self, response_time_ms: float,
                     effective_tok_s: float = 0.0,
                     breakdown: dict = None):
        self.system.total_queries_processed += 1
        self.system.total_response_time_ms += response_time_ms
        if effective_tok_s > 0:
            self.system.effective_tokens_per_second = (
                0.9 * self.system.effective_tokens_per_second +
                0.1 * effective_tok_s  # Exponential moving average
            )
        if breakdown:
            for stage, pct in breakdown.items():
                self.system.compute_breakdown[stage] = (
                    0.9 * self.system.compute_breakdown.get(stage, 0) +
                    0.1 * pct
                )

    def get_full_report(self) -> dict:
        return self.system.to_dict()

    def export_json(self, filepath: str = "logs/ira/metrics_report.json"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with self._export_lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.get_full_report(), f, indent=2, ensure_ascii=False)

    def reset(self):
        self.system = SystemMetrics()

def get_metric_collector() -> MetricCollector:
    return MetricCollector()


# Alias for backwards-compatibility: __init__.py imports IRAMetrics
IRAMetrics = SystemMetrics
