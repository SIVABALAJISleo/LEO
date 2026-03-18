"""
Global Memory Domination System
Every query must be logged, clustered, and made reusable.
This drives the system toward 95-99% avoidance over time by ensuring
that every inference becomes future reuse.
"""
import hashlib
import json
import logging
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

_MEMORY_CAP = 50_000  # Max entries before LRU eviction


class GlobalMemory:
    """
    Master memory store — logs every query with its resolution path.
    Clusters similar queries by shape_key to enable batch reuse.
    """

    def __init__(self):
        self._log: Dict[str, Dict[str, Any]] = {}       # query_hash → entry
        self._clusters: Dict[str, List[str]] = defaultdict(list)  # shape_key → [query_hashes]
        self._shape_answers: Dict[str, str] = {}        # shape_key → best answer seen

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:16]

    def log(
        self,
        query: str,
        answer: str,
        mode: str,
        shape_key: str,
        confidence: float,
        latency_ms: float = 0.0,
    ):
        """Log a query with its resolution metadata."""
        if len(self._log) >= _MEMORY_CAP:
            # Evict oldest 10%
            old_keys = list(self._log.keys())[:_MEMORY_CAP // 10]
            for k in old_keys:
                del self._log[k]

        qhash = self._hash(query)
        entry = {
            "query": query,
            "answer": answer,
            "mode": mode,
            "shape_key": shape_key,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "timestamp": time.time(),
            "reuses": 0,
        }
        self._log[qhash] = entry
        self._clusters[shape_key].append(qhash)

        # Keep best answer per shape_key (highest confidence)
        existing = self._shape_answers.get(shape_key)
        if not existing or confidence > self._log.get(self._hash(existing), {}).get("confidence", 0):
            self._shape_answers[shape_key] = answer

        logger.debug(f"memory_logged: shape={shape_key} mode={mode}")

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """Exact match lookup."""
        qhash = self._hash(query)
        entry = self._log.get(qhash)
        if entry:
            entry["reuses"] += 1
            logger.info(f"memory_hit: shape={entry['shape_key']} reuses={entry['reuses']}")
        return entry

    def best_answer_for_shape(self, shape_key: str) -> Optional[str]:
        """Return the best answer seen for this shape key."""
        return self._shape_answers.get(shape_key)

    def cluster_stats(self) -> Dict[str, int]:
        """Returns shape_key → cluster_size mapping."""
        return {k: len(v) for k, v in self._clusters.items()}

    def avoidance_stats(self) -> Dict[str, Any]:
        """Returns overall avoidance ratio across logged queries."""
        total = len(self._log)
        if total == 0:
            return {"total": 0, "avoidance_ratio": 0.0}
        model_calls = sum(1 for e in self._log.values() if e["mode"] in ("FULL_CALC", "LARGE_MODEL"))
        return {
            "total": total,
            "model_calls": model_calls,
            "avoidance_ratio": round(1.0 - model_calls / total, 3),
            "cluster_count": len(self._clusters),
            "shape_answers": len(self._shape_answers),
        }


global_memory = GlobalMemory()
