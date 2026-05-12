"""
backend/core/micro_parallel_processor.py

Micro-Parallel Processing Engine (AIS++ Module 7)
===================================================
Splits compound queries into N independent parts.
Processes all parts asynchronously in parallel (asyncio.gather).
Merges results into a unified answer.

This approximates parallel GPU-level processing entirely in software,
enabling multi-part queries to be resolved at the speed of the
SLOWEST single part — not the sum.

Rules:
  - Each part checked against memory before compute
  - Parts processed concurrently via asyncio.gather
  - Results merged in original order
  - Total latency ≈ max(part_latency) not sum(part_latency)
  - Stored individually per part → reused in future delta composition
"""
import logging
import asyncio
import time
import re
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Split corpus — ordered by specificity (most specific first)
SPLIT_PATTERNS = [
    r"\s+(?:and also|and then|additionally|furthermore|moreover)\s+",
    r"\s+(?:and|or|plus|as well as|along with)\s+",
    r"[,;]\s+",
    r"\s+-\s+",
]

MAX_PARTS    = 6     # maximum parts per query — don't over-split
MIN_PART_LEN = 8     # skip trivially short parts


def _split(query: str) -> List[str]:
    """
    Splits query into meaningful parts using hierarchical delimiters.
    Returns at least [query] if no good split point found.
    """
    for pattern in SPLIT_PATTERNS:
        parts = re.split(pattern, query.strip(), flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if len(p.strip()) >= MIN_PART_LEN]
        if len(parts) > 1:
            return parts[:MAX_PARTS]
    return [query]


class MicroParallelProcessor:
    """
    Software-level parallel query decomposition and merge.
    Achieves near-GPU parallel throughput for compound queries.
    """

    def __init__(self):
        self._total_resolved: int = 0
        self._from_memory: int = 0
        self._from_compute: int = 0

    async def resolve(
        self,
        query: str,
        global_memory,
        bg_compute,
        tenant_id: str,
        session_id: str,
        delta_engine,
    ) -> Optional[Dict[str, Any]]:
        """
        Main entry: splits query, resolves all parts concurrently,
        merges into a final response.

        Returns None if query is single-part (no benefit from splitting).
        """
        parts = _split(query)
        if len(parts) == 1:
            return None   # Nothing to parallelize

        start = time.monotonic()

        # Launch all part resolutions concurrently
        tasks = [
            self._resolve_part(part, global_memory, bg_compute, tenant_id, session_id)
            for part in parts
        ]
        results: List[Optional[Dict[str, Any]]] = await asyncio.gather(*tasks)
        elapsed_ms = (time.monotonic() - start) * 1000

        # Separate hits from misses
        hits   = [(p, r) for p, r in zip(parts, results) if r is not None]
        misses = [p for p, r in zip(parts, results) if r is None]

        if not hits:
            return None  # No parts resolved → fall through to full compute

        # Require at least majority coverage
        if len(hits) < max(1, len(parts) // 2):
            # Too many gaps — enqueue all missing parts
            for miss in misses:
                try:
                    asyncio.create_task(
                        bg_compute.enqueue(miss, tenant_id, "MICRO_PARALLEL", session_id)
                    )
                except Exception:
                    pass
            return None

        # Merge answers
        merged = self._merge(hits)
        self._total_resolved += 1

        # Store individual part results (for delta reuse)
        for part, result in hits:
            try:
                delta_engine.store_fragment(part, result["answer"], result.get("confidence", 0.9))
            except Exception:
                pass

        # Enqueue missing parts
        for miss in misses:
            try:
                asyncio.create_task(
                    bg_compute.enqueue(miss, tenant_id, "MICRO_PARALLEL", session_id)
                )
            except Exception:
                pass

        coverage = len(hits) / len(parts)
        confidence = min(r.get("confidence", 0.85) for _, r in hits) * coverage

        logger.info(
            f"micro_parallel.resolved: parts={len(parts)} "
            f"hits={len(hits)} elapsed={elapsed_ms:.1f}ms coverage={coverage:.0%}"
        )

        return {
            "answer":     merged,
            "mode":       "micro_parallel",
            "confidence": confidence,
            "parts_total":        len(parts),
            "parts_resolved":     len(hits),
            "parts_missing":      len(misses),
            "parallel_elapsed_ms": elapsed_ms,
        }

    async def _resolve_part(
        self,
        part: str,
        global_memory,
        bg_compute,
        tenant_id: str,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Tries to resolve a single part from memory. Non-blocking."""
        try:
            hit = await asyncio.to_thread(global_memory.lookup, part)
            if hit and hit.get("confidence", 0) >= 0.85:
                self._from_memory += 1
                return hit
        except Exception as exc:
            logger.debug(f"micro_parallel.part_lookup_error: '{part}' {exc}")
        return None

    def _merge(self, hits: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Merges part answers into a coherent compound response."""
        if len(hits) == 1:
            return hits[0][1]["answer"]

        sections: List[str] = []
        for i, (part, result) in enumerate(hits, 1):
            part_title = part.strip().rstrip("?!.").capitalize()
            sections.append(f"**{part_title}:**\n{result['answer']}")

        return "\n\n".join(sections)

    def stats(self) -> Dict[str, Any]:
        return {
            "total_resolved":   self._total_resolved,
            "from_memory":      self._from_memory,
            "from_compute":     self._from_compute,
        }


global_micro_parallel = MicroParallelProcessor()
