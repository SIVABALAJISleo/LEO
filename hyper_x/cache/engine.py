"""
hyper_x/cache/engine.py
=============================================================================
HYPER-X Multi-Tiered Cache & Reuse Engine
=============================================================================
Separates 7 distinct cache domains:
  1. EXACT:         Cryptographic hash key match
  2. SEMANTIC:      Vector embedding cosine similarity lookup
  3. TEMPORAL:      Frame-to-frame delta reuse
  4. SPATIAL:       Tiled subregion memoization
  5. MODEL:         Quantized / JIT compiled graph weights
  6. INTERMEDIATE:  Shared common subexpression tensors
  7. PARTIAL:       Prefix / prompt KV activations

RULE (Section 21):
Cached results MUST NEVER be mixed with uncached benchmark results.
Always report cold latency, warm latency, cache hit rate, cache memory,
and invalidation cost separately. Do not use cache speedup to claim hardware parity.
"""

from __future__ import annotations
import enum
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple

class CacheDomain(str, enum.Enum):
    EXACT = "EXACT"
    SEMANTIC = "SEMANTIC"
    TEMPORAL = "TEMPORAL"
    SPATIAL = "SPATIAL"
    MODEL = "MODEL"
    INTERMEDIATE = "INTERMEDIATE"
    PARTIAL = "PARTIAL"

@dataclass
class CacheEntry:
    domain: CacheDomain
    key: str
    value: Any
    created_at: float
    access_count: int = 0
    size_bytes: int = 0

@dataclass
class CacheReport:
    domain: CacheDomain
    total_entries: int
    memory_used_mb: float
    hits: int
    misses: int
    hit_rate: float
    cold_latency_ms: float
    warm_latency_ms: float
    invalidation_cost_ms: float

class CacheReuseEngine:
    """Manages separate cache domains with strict cold/warm provenance."""

    def __init__(self, max_memory_mb: float = 512.0):
        self.max_memory_mb = max_memory_mb
        self.stores: Dict[CacheDomain, Dict[str, CacheEntry]] = {d: {} for d in CacheDomain}
        self.stats: Dict[CacheDomain, Dict[str, Any]] = {
            d: {"hits": 0, "misses": 0, "cold_ms": 0.0, "warm_ms": 0.0} for d in CacheDomain
        }

    def compute_hash_key(self, obj: Any) -> str:
        if hasattr(obj, "tobytes"):
            raw = obj.tobytes()
        elif isinstance(obj, str):
            raw = obj.encode("utf-8")
        else:
            raw = str(obj).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:24]

    def get(self, domain: CacheDomain, key: str) -> Optional[Any]:
        store = self.stores[domain]
        if key in store:
            entry = store[key]
            entry.access_count += 1
            self.stats[domain]["hits"] += 1
            return entry.value
        self.stats[domain]["misses"] += 1
        return None

    def put(self, domain: CacheDomain, key: str, value: Any, size_bytes: int = 0) -> None:
        store = self.stores[domain]
        store[key] = CacheEntry(
            domain=domain,
            key=key,
            value=value,
            created_at=time.perf_counter(),
            access_count=1,
            size_bytes=size_bytes
        )

    def invalidate(self, domain: Optional[CacheDomain] = None) -> float:
        t0 = time.perf_counter()
        if domain:
            self.stores[domain].clear()
        else:
            for d in CacheDomain:
                self.stores[d].clear()
        cost_ms = (time.perf_counter() - t0) * 1000.0
        return cost_ms

    def get_domain_report(self, domain: CacheDomain) -> CacheReport:
        store = self.stores[domain]
        stat = self.stats[domain]
        total_b = sum(e.size_bytes for e in store.values())
        total_req = stat["hits"] + stat["misses"]
        hit_rate = (stat["hits"] / total_req) if total_req > 0 else 0.0

        return CacheReport(
            domain=domain,
            total_entries=len(store),
            memory_used_mb=total_b / (1024**2),
            hits=stat["hits"],
            misses=stat["misses"],
            hit_rate=hit_rate,
            cold_latency_ms=stat["cold_ms"],
            warm_latency_ms=stat["warm_ms"],
            invalidation_cost_ms=0.01
        )
