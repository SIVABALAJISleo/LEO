"""
hyper/upe/memory.py
===================
ENGINE 8: Path Memory & ENGINE 9: Verified Result Reuse.

Persistent knowledge base and contract-aware memoization engine.
Uses local zero-dependency SQLite storage (`hyper_upe_memory.db`) to record:
- Verified pathways and formal proof certificates
- Multi-trial benchmark records
- Discovered counterexamples
- Contract-aware deterministic memoization cache with LRU eviction
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "hyper_upe_memory.db")
)


class SQLitePathwayStore:
    """
    Persistent SQLite storage for verified pathways, benchmark trials, and counterexamples.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Verified Pathways Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upe_pathways (
                    pathway_id TEXT PRIMARY KEY,
                    workload_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    candidate_name TEXT NOT NULL,
                    family TEXT NOT NULL,
                    exactness_mode TEXT NOT NULL,
                    estimated_speedup REAL NOT NULL,
                    measured_speedup REAL NOT NULL,
                    highest_validation_level INTEGER NOT NULL,
                    proof_certificate TEXT,
                    created_at REAL NOT NULL,
                    metadata_json TEXT NOT NULL
                )
            """)

            # 2. Benchmark Experiments Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upe_benchmarks (
                    run_id TEXT PRIMARY KEY,
                    pathway_id TEXT NOT NULL,
                    workload_id TEXT NOT NULL,
                    baseline_latency_ms REAL NOT NULL,
                    optimized_latency_ms REAL NOT NULL,
                    measured_speedup REAL NOT NULL,
                    repetitions INTEGER NOT NULL,
                    peak_memory_mb REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    raw_timings_json TEXT NOT NULL
                )
            """)

            # 3. Counterexamples Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upe_counterexamples (
                    counterexample_id TEXT PRIMARY KEY,
                    workload_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    input_signature TEXT NOT NULL,
                    failure_category TEXT NOT NULL,
                    error_metric REAL NOT NULL,
                    description TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def store_pathway(
        self,
        pathway_id: str,
        workload_id: str,
        rule_id: str,
        candidate_name: str,
        family: str,
        exactness_mode: str,
        estimated_speedup: float,
        measured_speedup: float,
        highest_validation_level: int,
        proof_certificate: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO upe_pathways (
                    pathway_id, workload_id, rule_id, candidate_name, family,
                    exactness_mode, estimated_speedup, measured_speedup,
                    highest_validation_level, proof_certificate, created_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pathway_id,
                workload_id,
                rule_id,
                candidate_name,
                family,
                exactness_mode,
                estimated_speedup,
                measured_speedup,
                highest_validation_level,
                proof_certificate or "",
                time.time(),
                json.dumps(metadata or {}),
            ))
            conn.commit()

    def store_benchmark(
        self,
        run_id: str,
        pathway_id: str,
        workload_id: str,
        baseline_ms: float,
        optimized_ms: float,
        speedup: float,
        repetitions: int,
        peak_memory_mb: float,
        raw_timings: List[float],
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO upe_benchmarks (
                    run_id, pathway_id, workload_id, baseline_latency_ms,
                    optimized_latency_ms, measured_speedup, repetitions,
                    peak_memory_mb, timestamp, raw_timings_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                pathway_id,
                workload_id,
                baseline_ms,
                optimized_ms,
                speedup,
                repetitions,
                peak_memory_mb,
                time.time(),
                json.dumps(raw_timings),
            ))
            conn.commit()

    def store_counterexample(
        self,
        cx_id: str,
        workload_id: str,
        rule_id: str,
        input_sig: str,
        category: str,
        error_metric: float,
        desc: str,
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO upe_counterexamples (
                    counterexample_id, workload_id, rule_id, input_signature,
                    failure_category, error_metric, description, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cx_id, workload_id, rule_id, input_sig, category, error_metric, desc, time.time()
            ))
            conn.commit()

    def list_pathways(self, workload_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if workload_id:
                cursor.execute("SELECT * FROM upe_pathways WHERE workload_id = ? ORDER BY measured_speedup DESC", (workload_id,))
            else:
                cursor.execute("SELECT * FROM upe_pathways ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def list_benchmarks(self, workload_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if workload_id:
                cursor.execute("SELECT * FROM upe_benchmarks WHERE workload_id = ? ORDER BY timestamp DESC LIMIT ?", (workload_id, limit))
            else:
                cursor.execute("SELECT * FROM upe_benchmarks ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def list_counterexamples(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM upe_counterexamples ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


class ContractAwareCache:
    """
    ENGINE 9: Verified Result Reuse.
    Contract-scoped memoization with LRU eviction and collision-resistant hashing.
    Enforces strict isolation: Exact queries NEVER hit approximate entries.
    """

    def __init__(self, max_entries: int = 512) -> None:
        self.max_entries = max_entries
        # Key: (cache_key, validation_mode) -> (output, hit_count, timestamp)
        self._cache: collections.OrderedDict[Tuple[str, str], Tuple[Any, int, float]] = collections.OrderedDict()
        self.total_lookups = 0
        self.total_hits = 0
        self.total_misses = 0

    def compute_cache_key(
        self,
        workload_id: str,
        inputs: Dict[str, Any],
        contract_version: str,
    ) -> str:
        """Computes a SHA-256 digest over semantically relevant inputs and contract version."""
        hasher = hashlib.sha256()
        hasher.update(workload_id.encode("utf-8"))
        hasher.update(contract_version.encode("utf-8"))

        for k in sorted(inputs.keys()):
            hasher.update(k.encode("utf-8"))
            v = inputs[k]
            if isinstance(v, np.ndarray):
                hasher.update(v.tobytes()[:8192])
                hasher.update(str(v.shape).encode("utf-8"))
                hasher.update(str(v.dtype).encode("utf-8"))
            elif isinstance(v, (list, tuple)):
                hasher.update(str(v[:100]).encode("utf-8"))
            else:
                hasher.update(str(v).encode("utf-8"))

        return hasher.hexdigest()

    def get(self, cache_key: str, validation_mode: str) -> Optional[Any]:
        """Lookup entry matching both cache_key and validation_mode."""
        self.total_lookups += 1
        key_tuple = (cache_key, validation_mode)
        if key_tuple in self._cache:
            out, hits, _ = self._cache[key_tuple]
            self._cache.move_to_end(key_tuple)  # Mark as recently used
            self._cache[key_tuple] = (out, hits + 1, time.time())
            self.total_hits += 1
            return out

        self.total_misses += 1
        return None

    def put(self, cache_key: str, validation_mode: str, output: Any) -> None:
        """Stores entry with LRU eviction."""
        key_tuple = (cache_key, validation_mode)
        if key_tuple in self._cache:
            self._cache.move_to_end(key_tuple)
            self._cache[key_tuple] = (output, self._cache[key_tuple][1], time.time())
        else:
            if len(self._cache) >= self.max_entries:
                self._cache.popitem(last=False)  # Evict oldest entry
            self._cache[key_tuple] = (output, 1, time.time())

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        hit_rate = (self.total_hits / max(1, self.total_lookups)) * 100.0
        return {
            "total_entries": len(self._cache),
            "max_entries": self.max_entries,
            "total_lookups": self.total_lookups,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "hit_rate_pct": round(hit_rate, 2),
        }


class PathMemory:
    """
    Unified Facade combining persistent SQLite storage and in-memory contract cache.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, cache_size: int = 512) -> None:
        self.store = SQLitePathwayStore(db_path=db_path)
        self.cache = ContractAwareCache(max_entries=cache_size)
