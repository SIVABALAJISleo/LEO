"""
backend/optimization/self_optimizer.py
Subsystem 12: Continuous Self-Optimization Engine.
Runs as a background daemon that:
  1. Profiles every inference call (latency, memory, route)
  2. Detects bottlenecks (high-latency routes, low cache hit rate)
  3. Auto-tunes parameters (cache thresholds, speculation depth, exit thresholds)
  4. Logs findings for reproducible analysis
"""

import time
import threading
import statistics
import logging
import json
import os
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

_REPORT_PATH = os.path.join(os.path.dirname(__file__), "self_optimizer_report.json")


class ProfilerRecord:
    __slots__ = ("route", "latency_ms", "cache_hit", "layers_skipped", "timestamp")

    def __init__(self, route: str, latency_ms: float,
                 cache_hit: bool = False, layers_skipped: int = 0):
        self.route = route
        self.latency_ms = latency_ms
        self.cache_hit = cache_hit
        self.layers_skipped = layers_skipped
        self.timestamp = time.time()


class ContinuousSelfOptimizer:
    """
    Runtime profiler + bottleneck detector + auto-tuner.
    Attach to the Orchestrator to continuously improve the system.
    """

    # Rolling window: last 500 calls
    WINDOW = 500

    def __init__(self, optimization_interval_sec: float = 30.0):
        self.interval = optimization_interval_sec
        self.records: deque = deque(maxlen=self.WINDOW)
        self.running = False
        self._thread: Optional[threading.Thread] = None

        # Tunable parameters (modified by auto-tuner)
        self.params: Dict[str, Any] = {
            "cache_similarity_threshold": 0.95,
            "early_exit_threshold": 0.90,
            "speculate_k": 4,
            "max_context_tokens": 500,
        }

        # Per-route latency tracking
        self.route_latencies: Dict[str, deque] = defaultdict(lambda: deque(maxlen=200))

    def record(self, route: str, latency_ms: float,
               cache_hit: bool = False, layers_skipped: int = 0):
        """Called by orchestrator after every inference."""
        rec = ProfilerRecord(route, latency_ms, cache_hit, layers_skipped)
        self.records.append(rec)
        self.route_latencies[route].append(latency_ms)

    def get_live_stats(self) -> Dict[str, Any]:
        """Returns rolling-window statistics."""
        if not self.records:
            return {}

        all_latencies = [r.latency_ms for r in self.records]
        cache_hits = sum(1 for r in self.records if r.cache_hit)
        route_counts = defaultdict(int)
        for r in self.records:
            route_counts[r.route] += 1

        return {
            "total_calls": len(self.records),
            "avg_latency_ms": round(statistics.mean(all_latencies), 2),
            "p95_latency_ms": round(sorted(all_latencies)[int(len(all_latencies) * 0.95)], 2),
            "cache_hit_rate": round(cache_hits / len(self.records), 3),
            "route_distribution": dict(route_counts),
            "current_params": dict(self.params),
        }

    def _detect_bottlenecks(self) -> List[str]:
        """Identifies performance issues from current profiling window."""
        bottlenecks = []
        stats = self.get_live_stats()
        if not stats:
            return bottlenecks

        if stats["avg_latency_ms"] > 500:
            bottlenecks.append(f"HIGH_LATENCY: avg {stats['avg_latency_ms']}ms > 500ms threshold")

        if stats["cache_hit_rate"] < 0.20:
            bottlenecks.append(f"LOW_CACHE_HIT: {stats['cache_hit_rate']*100:.1f}% < 20% target")

        # Check if LARGE_MODEL is being over-used
        dist = stats.get("route_distribution", {})
        total = sum(dist.values()) or 1
        large_model_pct = dist.get("LARGE_MODEL", 0) / total
        if large_model_pct > 0.40:
            bottlenecks.append(
                f"OVERUSING_LARGE_MODEL: {large_model_pct*100:.1f}% of calls — expand rule/tiny model coverage"
            )

        return bottlenecks

    def _auto_tune(self, bottlenecks: List[str]):
        """Adjusts tunable parameters based on detected bottlenecks."""
        for b in bottlenecks:
            if "LOW_CACHE_HIT" in b:
                # Lower similarity threshold → more permissive cache matches
                old = self.params["cache_similarity_threshold"]
                self.params["cache_similarity_threshold"] = max(0.75, old - 0.02)
                logger.info(f"[SelfOptimizer] AUTO-TUNE: cache threshold {old:.2f} → {self.params['cache_similarity_threshold']:.2f}")

            elif "HIGH_LATENCY" in b:
                # Increase early exit aggressiveness
                old = self.params["early_exit_threshold"]
                self.params["early_exit_threshold"] = max(0.60, old - 0.05)
                logger.info(f"[SelfOptimizer] AUTO-TUNE: early_exit_threshold {old:.2f} → {self.params['early_exit_threshold']:.2f}")

    def _optimization_loop(self):
        while self.running:
            time.sleep(self.interval)
            if not self.records:
                continue

            stats = self.get_live_stats()
            bottlenecks = self._detect_bottlenecks()

            logger.info(
                f"[SelfOptimizer] Cycle: avg={stats.get('avg_latency_ms')}ms "
                f"p95={stats.get('p95_latency_ms')}ms "
                f"cache={stats.get('cache_hit_rate', 0)*100:.1f}% "
                f"bottlenecks={len(bottlenecks)}"
            )

            if bottlenecks:
                for b in bottlenecks:
                    logger.warning(f"[SelfOptimizer] BOTTLENECK: {b}")
                self._auto_tune(bottlenecks)

            # Persist report
            report = {"stats": stats, "bottlenecks": bottlenecks, "timestamp": time.time()}
            try:
                with open(_REPORT_PATH, "w") as f:
                    json.dump(report, f, indent=2)
            except Exception:
                pass

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self._thread.start()
        logger.info("[SelfOptimizer] Continuous Self-Optimization Engine started.")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
