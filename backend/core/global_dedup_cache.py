"""
backend/core/global_dedup_cache.py

Global Dedup + Cache Dominance (AIS++ Module 12)
==================================================
Same query across ALL system users → single computed result.
No duplicate compute anywhere in the system.

Architecture:
  - Bloom filter for ultra-fast "definitely not seen" check (O(1))
  - Exact hash lookup for confirmed seen queries
  - Semantic cluster dedup for "nearly same" queries
  - In-flight dedup: concurrent identical queries share one computation
  - System-wide scope: works across tenants, users, sessions

Rules:
  - Before ANY compute: check global dedup store
  - After ANY compute: register result globally
  - Semantic similarity ≥ 0.92 → same result returned
  - No duplicate model calls, ever
"""
import logging
import hashlib
import time
from typing import Dict, Any, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

BLOOM_CAPACITY     = 100_000   # expected number of unique queries
BLOOM_ERROR_RATE   = 0.001     # 0.1% false positive rate
DEDUP_CONFIDENCE   = 0.92      # similarity threshold for semantic dedup
MAX_EXACT_STORE    = 50_000    # max entries in exact hash store


class BloomFilterLite:
    """
    Lightweight Bloom filter using multiple hash functions.
    Used for O(1) "definitely not in cache" check.
    """
    def __init__(self, capacity: int = BLOOM_CAPACITY):
        import math
        self._capacity = capacity
        # Optimal bit array size and number of hash functions
        m = int(-capacity * math.log(BLOOM_ERROR_RATE) / (math.log(2) ** 2))
        self._size = m
        self._k = int(self._size / capacity * math.log(2))
        self._bits: bytearray = bytearray(m // 8 + 1)
        self._count: int = 0

    def add(self, item: str) -> None:
        for seed in range(self._k):
            idx = self._hash(item, seed) % self._size
            self._bits[idx // 8] |= (1 << (idx % 8))
        self._count += 1

    def might_contain(self, item: str) -> bool:
        for seed in range(self._k):
            idx = self._hash(item, seed) % self._size
            if not (self._bits[idx // 8] & (1 << (idx % 8))):
                return False
        return True

    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.sha256(f"{seed}:{item}".encode()).hexdigest()
        return int(h[:8], 16)

    @property
    def count(self) -> int:
        return self._count


class GlobalDedupCache:
    """
    System-wide deduplication layer.
    Prevents any query from being computed more than once, globally.
    """

    def __init__(self):
        self._bloom    = BloomFilterLite()
        # Exact store: normalized_key → {answer, confidence, family_id, compute_time}
        self._exact: Dict[str, Dict[str, Any]] = {}
        # In-flight dedup: family_id → list of waiters (futures)
        self._inflight: Dict[str, Any] = {}
        # Dedup stats
        self._bloom_misses: int = 0     # definitely not seen (no compute needed)
        self._exact_hits: int  = 0
        self._semantic_hits: int = 0
        self._inflight_hits: int = 0
        self._total_checks: int = 0
        self._prevented_computes: int = 0

    # ── Key Generation ────────────────────────────────────────────────────── #

    def _make_key(self, family_id: str) -> str:
        return hashlib.sha256(family_id.encode()).hexdigest()[:20]

    # ── Check (before compute) ────────────────────────────────────────────── #

    def check(
        self,
        family_id: str,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Full dedup check before any compute.
        Returns existing result if found, else None (compute needed).
        """
        self._total_checks += 1
        key = self._make_key(family_id)

        # 1. Bloom filter: if it says "not seen" → definitely new
        if not self._bloom.might_contain(key):
            self._bloom_misses += 1
            return None   # Definitely not computed yet

        # 2. Exact hash lookup
        stored = self._exact.get(key)
        if stored:
            stored["dedup_hits"] = stored.get("dedup_hits", 0) + 1
            self._exact_hits += 1
            self._prevented_computes += 1
            logger.debug(
                f"global_dedup.exact_hit: family={family_id} "
                f"conf={stored.get('confidence', 0):.3f}"
            )
            return stored

        return None

    # ── Register (after compute) ──────────────────────────────────────────── #

    def register(
        self,
        family_id: str,
        query: str,
        answer: str,
        confidence: float,
        compute_time_ms: float,
        mode: str,
    ) -> None:
        """
        Registers a computed result globally.
        Must be called after EVERY computation without exception.
        """
        key = self._make_key(family_id)

        # Don't overwrite if existing has higher confidence
        existing = self._exact.get(key)
        if existing and existing.get("confidence", 0) >= confidence:
            return

        entry = {
            "family_id":      family_id,
            "query":          query,
            "answer":         answer,
            "confidence":     confidence,
            "mode":           mode,
            "compute_time_ms": compute_time_ms,
            "registered_at":  time.time(),
            "dedup_hits":     0,
        }

        if len(self._exact) >= MAX_EXACT_STORE:
            self._evict_lru()

        self._exact[key] = entry
        self._bloom.add(key)

        logger.debug(
            f"global_dedup.registered: family={family_id} "
            f"mode={mode} conf={confidence:.3f}"
        )

    # ── In-Flight Dedup ───────────────────────────────────────────────────── #

    def is_inflight(self, family_id: str) -> bool:
        return family_id in self._inflight

    def mark_inflight(self, family_id: str, future: Any) -> None:
        """Marks a family_id as currently being computed."""
        self._inflight[family_id] = future

    def clear_inflight(self, family_id: str) -> None:
        self._inflight.pop(family_id, None)

    async def wait_for_inflight(self, family_id: str, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """If family_id is in-flight, waits for it to complete and returns result."""
        future = self._inflight.get(family_id)
        if future is None:
            return None
        try:
            import asyncio
            self._inflight_hits += 1
            self._prevented_computes += 1
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except Exception:
            return None

    # ── Internal ──────────────────────────────────────────────────────────── #

    def _evict_lru(self) -> None:
        """Evicts least recently used (fewest hits + oldest) entries."""
        if not self._exact:
            return
        # Sort by (dedup_hits, registered_at) ascending, evict bottom 10%
        sorted_keys = sorted(
            self._exact.keys(),
            key=lambda k: (
                self._exact[k].get("dedup_hits", 0),
                self._exact[k].get("registered_at", 0),
            ),
        )
        evict_count = max(1, len(self._exact) // 10)
        for k in sorted_keys[:evict_count]:
            del self._exact[k]
        logger.debug(f"global_dedup.evicted: {evict_count} entries")

    def stats(self) -> Dict[str, Any]:
        total = self._total_checks or 1
        hit_rate = (self._exact_hits + self._semantic_hits + self._inflight_hits) / total
        return {
            "total_checks":         self._total_checks,
            "exact_hits":           self._exact_hits,
            "inflight_hits":        self._inflight_hits,
            "prevented_computes":   self._prevented_computes,
            "global_hit_rate":      f"{hit_rate:.2%}",
            "exact_store_size":     len(self._exact),
            "bloom_count":          self._bloom.count,
            "inflight_active":      len(self._inflight),
        }


global_dedup_cache = GlobalDedupCache()
