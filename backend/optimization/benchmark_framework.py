"""
backend/optimization/benchmark_framework.py
Subsystem 18: Benchmark Framework.
Measures true generation tokens/sec, retrieval latency, cache hit rate,
memory usage, CPU utilization, and end-to-end latency.
Generates reproducible JSON reports. Never fabricates values.
"""

import time
import os
import json
import logging
import psutil
from typing import Callable, Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BenchmarkTimer:
    """High-resolution context manager timer."""
    def __init__(self, label: str):
        self.label = label
        self.elapsed_ms = 0.0

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self._t0) * 1000.0


class BenchmarkFramework:
    """
    Collects and reports reproducible runtime benchmarks.
    All measurements are real wall-clock timings from psutil / perf_counter.
    """
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self._process = psutil.Process(os.getpid())

    def _snapshot_resources(self) -> Dict[str, float]:
        mem = self._process.memory_info()
        cpu = psutil.cpu_percent(interval=None)
        return {
            "rss_mb": mem.rss / (1024 ** 2),
            "cpu_percent": cpu,
            "available_ram_gb": psutil.virtual_memory().available / (1024 ** 3)
        }

    def benchmark_latency(self, label: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Measures wall-clock latency of a synchronous function call."""
        before = self._snapshot_resources()
        with BenchmarkTimer(label) as timer:
            result = func(*args, **kwargs)
        after = self._snapshot_resources()

        record = {
            "benchmark": label,
            "latency_ms": round(timer.elapsed_ms, 3),
            "ram_delta_mb": round(after["rss_mb"] - before["rss_mb"], 2),
            "cpu_before": before["cpu_percent"],
            "cpu_after": after["cpu_percent"],
            "result_preview": str(result)[:120] if result is not None else None
        }
        self.results.append(record)
        logger.info(f"[Benchmark] {label}: {timer.elapsed_ms:.2f}ms | ΔMem: {record['ram_delta_mb']}MB")
        return record

    def benchmark_cache(self, label: str, cache_check: Callable, cache_populate: Callable,
                        queries: List[str]) -> Dict[str, Any]:
        """Measures cache hit rate across a query set."""
        hits, misses = 0, 0

        # Populate with first half
        for q in queries[:len(queries) // 2]:
            cache_populate(q, f"Answer for: {q}")

        # Check all
        for q in queries:
            res = cache_check(q)
            if res is not None:
                hits += 1
            else:
                misses += 1

        rate = hits / len(queries) if queries else 0.0
        record = {
            "benchmark": label,
            "total_queries": len(queries),
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate_pct": round(rate * 100, 1)
        }
        self.results.append(record)
        logger.info(f"[Benchmark] {label}: Hit Rate = {rate*100:.1f}% ({hits}/{len(queries)})")
        return record

    def benchmark_throughput(self, label: str, func: Callable, inputs: List[Any],
                             unit: str = "items") -> Dict[str, Any]:
        """Measures throughput: items processed per second."""
        with BenchmarkTimer(label) as timer:
            for inp in inputs:
                func(inp)

        total_items = len(inputs)
        throughput = total_items / (timer.elapsed_ms / 1000.0) if timer.elapsed_ms > 0 else 0
        record = {
            "benchmark": label,
            "total_items": total_items,
            "total_ms": round(timer.elapsed_ms, 2),
            "throughput_per_sec": round(throughput, 1),
            "unit": unit
        }
        self.results.append(record)
        logger.info(f"[Benchmark] {label}: {throughput:.1f} {unit}/sec")
        return record

    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Produces a structured, reproducible JSON benchmark report."""
        report = {
            "system": {
                "cpu_count": psutil.cpu_count(logical=True),
                "total_ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
                "platform": os.name
            },
            "benchmarks": self.results,
            "summary": {
                "total_benchmarks": len(self.results),
                "avg_latency_ms": round(
                    sum(r["latency_ms"] for r in self.results if "latency_ms" in r) /
                    max(1, sum(1 for r in self.results if "latency_ms" in r)), 2
                )
            }
        }
        if output_path:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Benchmark report saved to {output_path}")
        return report
