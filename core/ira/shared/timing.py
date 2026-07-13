"""
Precision timing utilities for IRA.
Uses time.perf_counter() for nanosecond-level accuracy.
Every operation in IRA is timed — no exceptions.
"""
import time
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import json
import os

@dataclass
class TimingSample:
    """A single timing measurement."""
    name: str
    start_ns: int
    end_ns: int
    duration_ms: float
    thread_id: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 6),
            "thread_id": self.thread_id,
            "metadata": self.metadata
        }

class PrecisionTimer:
    """
    High-precision timer for measuring individual operations.
    Usage:
        timer = PrecisionTimer("qsm_lookup")
        # ... do work ...
        elapsed = timer.stop()  # returns ms
    """
    def __init__(self, name: str, metadata: dict = None):
        self.name = name
        self.metadata = metadata or {}
        self.start_ns: int = 0
        self.end_ns: int = 0
        self._stopped = False

    def start(self) -> 'PrecisionTimer':
        self.start_ns = time.perf_counter_ns()
        self._stopped = False
        return self

    def stop(self) -> float:
        if self._stopped:
            return self.duration_ms
        self.end_ns = time.perf_counter_ns()
        self._stopped = True
        return self.duration_ms

    @property
    def duration_ns(self) -> int:
        if not self._stopped:
            self.stop()
        return self.end_ns - self.start_ns

    @property
    def duration_ms(self) -> float:
        return self.duration_ns / 1_000_000.0

    @property
    def duration_us(self) -> float:
        return self.duration_ns / 1_000.0

    def to_sample(self) -> TimingSample:
        return TimingSample(
            name=self.name,
            start_ns=self.start_ns,
            end_ns=self.end_ns,
            duration_ms=self.duration_ms,
            thread_id=threading.get_ident(),
            metadata=self.metadata
        )

@contextmanager
def measure(operation_name: str, metadata: dict = None):
    """
    Context manager for timing code blocks.
    Usage:
        with measure("qsm_lookup") as t:
            result = qsm.retrieve(query)
        print(f"Lookup took {t.duration_ms:.3f}ms")
    """
    timer = PrecisionTimer(operation_name, metadata).start()
    try:
        yield timer
    finally:
        timer.stop()

class TimerManager:
    """
    Manages all timing samples across the entire IRA system.
    Thread-safe. Persists to disk for analysis.
    """
    def __init__(self, max_samples: int = 100000):
        self.max_samples = max_samples
        self._samples: List[TimingSample] = []
        self._lock = threading.Lock()
        self._counters: Dict[str, float] = {}
        self._counter_lock = threading.Lock()

    def record(self, sample: TimingSample):
        with self._lock:
            if len(self._samples) >= self.max_samples:
                self._samples = self._samples[self.max_samples // 2:]
            self._samples.append(sample)

    def increment_counter(self, name: str, value: float = 1.0):
        with self._counter_lock:
            self._counters[name] = self._counters.get(name, 0.0) + value

    def get_counter(self, name: str) -> float:
        with self._counter_lock:
            return self._counters.get(name, 0.0)

    def get_stats(self, operation_name: str) -> dict:
        """Get timing statistics for a specific operation."""
        with self._lock:
            samples = [s for s in self._samples if s.name == operation_name]
        if not samples:
            return {"count": 0}
        durations = [s.duration_ms for s in samples]
        return {
            "count": len(durations),
            "min_ms": round(min(durations), 6),
            "max_ms": round(max(durations), 6),
            "mean_ms": round(sum(durations) / len(durations), 6),
            "p50_ms": round(sorted(durations)[len(durations)//2], 6),
            "p95_ms": round(sorted(durations)[int(len(durations)*0.95)], 6),
            "p99_ms": round(sorted(durations)[int(len(durations)*0.99)], 6),
            "total_ms": round(sum(durations), 6)
        }

    def get_all_stats(self) -> dict:
        """Get stats for ALL recorded operations."""
        with self._lock:
            names = set(s.name for s in self._samples)
        return {name: self.get_stats(name) for name in names}

    def export_json(self, filepath: str):
        """Export all samples to JSON for analysis."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "samples": [s.to_dict() for s in self._samples],
                "counters": self._counters,
                "stats": self.get_all_stats()
            }, f, indent=2, ensure_ascii=False)

    def clear(self):
        with self._lock:
            self._samples.clear()
        with self._counter_lock:
            self._counters.clear()

# Global singleton
_global_timer_manager: Optional[TimerManager] = None

def get_global_timer_manager() -> TimerManager:
    global _global_timer_manager
    if _global_timer_manager is None:
        _global_timer_manager = TimerManager()
    return _global_timer_manager
