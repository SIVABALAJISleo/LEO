"""
backend/core/experience_optimizer.py

Experience Prioritization Engine (AIS++ Module 10)
====================================================
Optimizes for PERCEIVED speed, not just raw latency.

Strategies:
  1. Immediate ACK — respond with partial token in <5ms
  2. Path Promotion — measure every route's P95 latency;
     faster routes elevated in priority automatically
  3. Streaming refinement — stream skeleton → full answer
  4. Path demotion — routes consistently >100ms are deprioritized
  5. Latency budget enforcement — hard ceiling per stage

Perceived latency rule:
  User receives SOMETHING in <5ms, always.
  Full answer delivered within budget.
  System learns which paths are fastest per intent/entity.

Rules:
  - No path prioritized without real latency data
  - Promotion/demotion updates after every 10 calls per path
  - Hard ceiling: 200ms absolute (BUG if exceeded)
"""
import logging
import time
import json
import os
from typing import Dict, Any, List, Optional
from collections import deque

logger = logging.getLogger(__name__)

LEARN_AFTER_N      = 10     # update path priority after N observations
PROMOTE_THRESHOLD  = 20.0   # ms — paths faster than this are promoted
DEMOTE_THRESHOLD   = 100.0  # ms — paths slower than this are demoted
ABSOLUTE_CEILING   = 200.0  # ms — hard bug threshold
PRIORITY_FILE      = os.path.join(os.getcwd(), "data", "path_priorities.json")


class PathStats:
    """Latency statistics for a single path/mode."""
    __slots__ = ["name", "latencies", "priority", "calls"]

    def __init__(self, name: str):
        self.name      = name
        self.latencies = deque(maxlen=200)
        self.priority  = 5        # 1 = highest, 10 = lowest
        self.calls     = 0

    def record(self, latency_ms: float) -> None:
        self.latencies.append(latency_ms)
        self.calls += 1

    @property
    def p95(self) -> float:
        if not self.latencies:
            return 999.0
        s = sorted(self.latencies)
        return s[int(len(s) * 0.95)]

    @property
    def mean(self) -> float:
        if not self.latencies:
            return 999.0
        return sum(self.latencies) / len(self.latencies)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name":     self.name,
            "priority": self.priority,
            "calls":    self.calls,
            "mean_ms":  round(self.mean, 2),
            "p95_ms":   round(self.p95, 2),
        }


class ExperienceOptimizer:
    """
    Tracks per-path latency and dynamically reorders execution priority
    to maximize perceived speed.
    """

    def __init__(self):
        self._paths: Dict[str, PathStats] = {}
        self._ack_count: int   = 0
        self._violations: int  = 0
        self._load()

    # ── Instant ACK ───────────────────────────────────────────────────────── #

    def get_instant_ack(self, query: str, request_id: str) -> Dict[str, Any]:
        """
        Returns sub-5ms response body with query echo + processing signal.
        Always call this first — gives client instant feedback.
        """
        self._ack_count += 1
        return {
            "request_id":     request_id,
            "status":         "processing",
            "query_received": query[:80],
            "ack_ms":         time.time(),
            "message":        "Query received. Answer follows immediately.",
        }

    # ── Latency Recording + Learn ──────────────────────────────────────────── #

    def record(self, path: str, latency_ms: float) -> None:
        """Record a latency observation for a path and update priority."""
        if path not in self._paths:
            self._paths[path] = PathStats(path)

        stats = self._paths[path]
        stats.record(latency_ms)

        # Check hard ceiling violation
        if latency_ms > ABSOLUTE_CEILING:
            self._violations += 1
            logger.error(
                f"EXPERIENCE_VIOLATION: path={path} "
                f"latency={latency_ms:.1f}ms > {ABSOLUTE_CEILING}ms ceiling — BUG"
            )

        # Recompute priority every LEARN_AFTER_N calls
        if stats.calls % LEARN_AFTER_N == 0:
            self._update_priority(stats)

    def _update_priority(self, stats: PathStats) -> None:
        """Promotes or demotes a path based on its P95 latency."""
        p95 = stats.p95
        old = stats.priority

        if p95 < PROMOTE_THRESHOLD:
            stats.priority = max(1, stats.priority - 1)   # promote
        elif p95 > DEMOTE_THRESHOLD:
            stats.priority = min(10, stats.priority + 1)  # demote

        if stats.priority != old:
            direction = "PROMOTED" if stats.priority < old else "DEMOTED"
            logger.info(
                f"experience.{direction.lower()}: path={stats.name} "
                f"p95={p95:.1f}ms priority={old}→{stats.priority}"
            )
        self._save()

    # ── Path Priority Ordering ─────────────────────────────────────────────── #

    def get_ordered_paths(self, candidate_paths: List[str]) -> List[str]:
        """
        Returns candidate_paths sorted by their learned priority (fastest first).
        Used by the pipeline to try fastest paths first.
        """
        def _priority(p: str) -> int:
            return self._paths.get(p, PathStats(p)).priority

        return sorted(candidate_paths, key=_priority)

    def get_fastest_path(self) -> Optional[str]:
        """Returns the currently fastest (priority=1) path name, if any."""
        if not self._paths:
            return None
        return min(self._paths.values(), key=lambda s: s.priority).name

    # ── Streaming Refinement ──────────────────────────────────────────────── #

    async def stream_skeleton_then_refine(
        self,
        query: str,
        skeleton: str,
        full_answer_coro,
    ):
        """
        Async generator: immediately yields skeleton, then yields
        the full refined answer once the coroutine completes.
        Use with FastAPI StreamingResponse.
        """
        yield skeleton + "\n\n[Computing full answer...]\n"
        try:
            import asyncio
            full = await asyncio.wait_for(full_answer_coro, timeout=5.0)
            yield "\n[FULL ANSWER]\n" + (full or "")
        except asyncio.TimeoutError:
            yield "\n[Full answer delayed — check /api/v1/updates for update.]\n"
        except Exception as exc:
            logger.warning(f"experience.stream_error: {exc}")

    # ── Stats + Observability ─────────────────────────────────────────────── #

    def get_path_report(self) -> List[Dict[str, Any]]:
        """Returns latency report for all tracked paths, sorted by priority."""
        return sorted(
            [s.to_dict() for s in self._paths.values()],
            key=lambda x: x["priority"],
        )

    def stats(self) -> Dict[str, Any]:
        return {
            "paths_tracked":    len(self._paths),
            "ack_count":        self._ack_count,
            "ceiling_violations": self._violations,
            "fastest_path":     self.get_fastest_path(),
            "path_report":      self.get_path_report(),
        }

    # ── Persistence ───────────────────────────────────────────────────────── #

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(PRIORITY_FILE), exist_ok=True)
            data = {name: {"priority": s.priority, "calls": s.calls}
                    for name, s in self._paths.items()}
            with open(PRIORITY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _load(self) -> None:
        if not os.path.exists(PRIORITY_FILE):
            return
        try:
            with open(PRIORITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, d in data.items():
                s = PathStats(name)
                s.priority = d.get("priority", 5)
                s.calls    = d.get("calls", 0)
                self._paths[name] = s
            logger.info(f"experience.loaded: {len(self._paths)} paths")
        except Exception:
            pass


global_experience_optimizer = ExperienceOptimizer()
