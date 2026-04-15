"""
backend/predictive/probability_engine.py

Probability-Driven Precompute Engine (AIS++ Module 3)
======================================================
Assigns probability scores to queries.
Maintains a priority queue — highest-probability queries precomputed first.
Ensures the most likely user queries are always warm in cache.

Probability factors:
  - Historical frequency (how often this query was asked)
  - Session trend (recently active families)
  - Entity popularity (globally hot entities)
  - Temporal relevance (recent = higher probability)
  - Semantic cluster density (many related cached queries = hot cluster)

Rules:
  - Only queries with probability >= PRECOMPUTE_THRESHOLD are enqueued
  - Priority queue ordered by probability score (descending)
  - Re-scoring happens on every new query arrival
  - Never computes what's already cached
"""
import logging
import asyncio
import time
import heapq
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

PRECOMPUTE_THRESHOLD   = 0.30   # minimum probability to warrant precompute
MAX_QUEUE_SIZE         = 500    # cap priority queue
FREQUENCY_WEIGHT       = 0.40
RECENCY_WEIGHT         = 0.25
CLUSTER_DENSITY_WEIGHT = 0.20
ENTITY_POPULARITY_WEIGHT = 0.15


class ProbabilityEntry:
    """Priority queue entry. Higher probability = higher priority."""
    __slots__ = ["score", "query", "family_id", "entity", "intent", "created_at"]

    def __init__(self, score: float, query: str, family_id: str, entity: str, intent: str):
        self.score      = score
        self.query      = query
        self.family_id  = family_id
        self.entity     = entity
        self.intent     = intent
        self.created_at = time.time()

    # Heap is a min-heap, so negate score for max-first ordering
    def __lt__(self, other: "ProbabilityEntry") -> bool:
        return self.score > other.score


class ProbabilityEngine:
    """
    Assigns computed probability scores to queries and drives
    proactive precompute in priority order.
    """

    def __init__(self):
        # Frequency counters per family_id
        self._frequency: Dict[str, int] = defaultdict(int)
        # Last-seen timestamp per family_id
        self._last_seen: Dict[str, float] = {}
        # Entity global popularity score
        self._entity_popularity: Dict[str, float] = defaultdict(float)
        # Priority queue (min-heap, negated score for max-first)
        self._queue: List[ProbabilityEntry] = []
        # Set of family_ids currently in queue (for O(1) membership check)
        self._in_queue: set = set()
        # Total precompute jobs dispatched
        self._dispatched: int = 0

    # ── Scoring ────────────────────────────────────────────────────────────── #

    def score(
        self,
        family_id: str,
        entity: str,
        intent: str,
        cluster_density: int = 0,
    ) -> float:
        """
        Computes a probability score in [0, 1] for the given family_id.
        Higher = more likely to be asked = higher precompute priority.
        """
        freq = self._frequency.get(family_id, 0)
        freq_score = min(freq / 20.0, 1.0)  # Normalize: 20+ requests → 1.0

        # Recency: queries seen in last 5 min are hot
        last = self._last_seen.get(family_id)
        if last:
            age_secs = time.time() - last
            recency_score = max(0.0, 1.0 - age_secs / 300.0)
        else:
            recency_score = 0.0

        # Cluster density: more neighbors → higher potential reuse
        density_score = min(cluster_density / 10.0, 1.0)

        # Entity popularity
        entity_score = min(self._entity_popularity.get(entity.upper(), 0.0), 1.0)

        probability = (
            FREQUENCY_WEIGHT        * freq_score
            + RECENCY_WEIGHT        * recency_score
            + CLUSTER_DENSITY_WEIGHT * density_score
            + ENTITY_POPULARITY_WEIGHT * entity_score
        )
        return round(probability, 4)

    def record_query(self, family_id: str, entity: str) -> None:
        """Call whenever a query arrives — updates frequency and recency."""
        self._frequency[family_id] += 1
        self._last_seen[family_id] = time.time()
        self._entity_popularity[entity.upper()] += 0.1

    def enqueue_if_worthy(
        self,
        query: str,
        family_id: str,
        entity: str,
        intent: str,
        cluster_density: int = 0,
    ) -> Optional[float]:
        """
        Scores the query and adds to priority queue if probability
        exceeds PRECOMPUTE_THRESHOLD and queue is not full.
        Returns the score if enqueued, None otherwise.
        """
        if family_id in self._in_queue:
            return None
        if len(self._queue) >= MAX_QUEUE_SIZE:
            return None

        prob = self.score(family_id, entity, intent, cluster_density)
        if prob < PRECOMPUTE_THRESHOLD:
            return None

        entry = ProbabilityEntry(prob, query, family_id, entity, intent)
        heapq.heappush(self._queue, entry)
        self._in_queue.add(family_id)

        logger.debug(f"prob_engine.enqueued: family={family_id} prob={prob:.3f}")
        return prob

    # ── Dispatch Worker ───────────────────────────────────────────────────── #

    async def dispatch_top_k(
        self,
        k: int,
        bg_compute,
        tenant_id: str,
        global_memory,
    ) -> int:
        """
        Drains top-k entries from priority queue, skips already-cached.
        Returns count of jobs actually dispatched.
        """
        dispatched = 0
        processed = 0

        while self._queue and processed < k:
            entry = heapq.heappop(self._queue)
            self._in_queue.discard(entry.family_id)
            processed += 1

            # Skip already cached
            try:
                existing = global_memory.lookup(entry.query)
                if existing and existing.get("confidence", 0) >= 0.95:
                    continue
            except Exception:
                pass

            # Enqueue for background precompute
            try:
                asyncio.create_task(
                    bg_compute.enqueue(
                        entry.query,
                        tenant_id,
                        "PROBABILITY_ENGINE",
                        "system",
                        priority="probability",
                    )
                )
                dispatched += 1
                self._dispatched += 1
            except Exception as exc:
                logger.warning(f"prob_engine.dispatch_error: {exc}")

        if dispatched:
            logger.info(f"prob_engine.dispatched: {dispatched} jobs from queue")
        return dispatched

    async def run_continuous(
        self,
        bg_compute,
        global_memory,
        tenant_id: str = "default",
        interval_sec: float = 5.0,
        batch_size: int = 10,
    ) -> None:
        """
        Background coroutine: continuously drains high-probability
        queries from the priority queue.
        """
        logger.info("prob_engine.continuous_worker: started")
        while True:
            try:
                if self._queue:
                    await self.dispatch_top_k(batch_size, bg_compute, tenant_id, global_memory)
            except Exception as exc:
                logger.error(f"prob_engine.run_error: {exc}")
            await asyncio.sleep(interval_sec)

    def get_top_k_probabilities(self, k: int = 10) -> List[Dict[str, Any]]:
        """Returns top-k queue entries for observability."""
        sorted_q = sorted(self._queue, reverse=False)  # min-heap, but ProbabilityEntry.__lt__ is max-first
        return [
            {
                "query": e.query,
                "family_id": e.family_id,
                "entity": e.entity,
                "intent": e.intent,
                "score": e.score,
            }
            for e in sorted_q[:k]
        ]

    def stats(self) -> Dict[str, Any]:
        return {
            "queue_size":        len(self._queue),
            "unique_families":   len(self._frequency),
            "total_dispatched":  self._dispatched,
            "top_entities":      sorted(
                self._entity_popularity.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


global_probability_engine = ProbabilityEngine()
