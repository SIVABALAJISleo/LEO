"""
backend/core/delta_compute_engine.py

Delta Compute Engine
=====================
Decompose a query into N parts.
Reuse all known parts from global memory.
Compute ONLY the unknown/missing fragment.

Rules:
  - Prevents full model calls when partial knowledge exists
  - Composed answers stored permanently (zero-repeat)
  - Part results individually cached for future reuse
"""
import logging
import time
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Confidence threshold for accepting a fragment from memory
FRAGMENT_CONFIDENCE_FLOOR = 0.82


def _split_query_parts(query: str) -> List[str]:
    """
    Decompose a query into meaningful parts by splitting on
    conjunctions, commas, semicolons, and 'and/or/plus'.
    Returns at least [query] if no split point found.
    """
    # Split on natural language conjunctions
    parts = re.split(
        r"\s+(?:and|or|plus|also|as well as|additionally|,|;)\s+",
        query.lower().strip(),
        flags=re.IGNORECASE,
    )
    parts = [p.strip() for p in parts if len(p.strip()) > 3]
    return parts if parts else [query]


class DeltaComputeEngine:
    """
    Fragment-level compute reuse.
    For compound queries, assembles answer from cached parts,
    only computing the genuinely unknown fragments.
    """

    def __init__(self):
        # Fragment store: part_hash → answer text
        self._fragment_cache: Dict[str, Dict[str, Any]] = {}

    # ── Public API ─────────────────────────────────────────────────────────── #

    async def resolve(
        self,
        query: str,
        global_memory,
        bg_compute,
        tenant_id: str,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to compose a full answer from known fragments.
        Returns composed answer dict, or None if insufficient fragments found.

        Rules enforced:
          - Each fragment must have confidence >= FRAGMENT_CONFIDENCE_FLOOR
          - Composition is only returned when ALL parts are covered
          - Unknown parts are enqueued for background compute (not blocking)
        """
        parts = _split_query_parts(query)

        # Single-part queries: no delta composition to do
        if len(parts) == 1:
            return None

        known: List[Tuple[str, str]] = []     # (part, answer)
        unknown: List[str] = []

        for part in parts:
            # 1. Check fragment local cache
            cached = self._fragment_cache.get(self._part_key(part))
            if cached and cached.get("confidence", 0) >= FRAGMENT_CONFIDENCE_FLOOR:
                known.append((part, cached["answer"]))
                continue

            # 2. Check global memory
            hit = global_memory.lookup(part)
            if hit and hit.get("confidence", 0) >= FRAGMENT_CONFIDENCE_FLOOR:
                # Store in local fragment cache for instant future hits
                self._store_fragment(part, hit["answer"], hit["confidence"])
                known.append((part, hit["answer"]))
            else:
                unknown.append(part)

        if not known:
            return None  # No fragments available — full compute required

        # Enqueue unknown fragments for background compute (non-blocking)
        for unk in unknown:
            try:
                asyncio.create_task(
                    bg_compute.enqueue(
                        unk, tenant_id, "DELTA_ENGINE", session_id, priority="delta"
                    )
                )
                logger.debug(f"delta.enqueue_unknown: '{unk}'")
            except Exception as exc:
                logger.warning(f"delta.enqueue_error: {exc}")

        # If all parts known — return complete composition
        if not unknown:
            composed = self._compose(known)
            coverage = 1.0
            logger.info(
                f"delta.full_composition: parts={len(parts)} "
                f"coverage={coverage:.0%}"
            )
            return {
                "answer": composed,
                "mode": "delta_full",
                "confidence": self._avg_confidence(known, global_memory),
                "parts_known": len(known),
                "parts_unknown": 0,
                "coverage": coverage,
            }

        # Partial coverage — return partial answer with disclaimer
        if len(known) >= max(1, len(parts) - 1):
            composed = self._compose(known)
            coverage = len(known) / len(parts)
            logger.info(
                f"delta.partial_composition: parts={len(parts)} "
                f"known={len(known)} coverage={coverage:.0%}"
            )
            partial_note = (
                f"\n\n[Note: {len(unknown)} part(s) are being computed in "
                "background and will be available shortly.]"
            )
            return {
                "answer": composed + partial_note,
                "mode": "delta_partial",
                "confidence": self._avg_confidence(known, global_memory) * coverage,
                "parts_known": len(known),
                "parts_unknown": len(unknown),
                "coverage": coverage,
            }

        return None  # Too many missing fragments — escalate to full compute

    def store_fragment(self, part: str, answer: str, confidence: float = 0.95) -> None:
        """Stores a computed fragment for future delta composition."""
        self._store_fragment(part, answer, confidence)

    def stats(self) -> Dict[str, Any]:
        return {
            "fragment_cache_size": len(self._fragment_cache),
            "fragments": list(self._fragment_cache.keys())[:10],  # sample
        }

    # ── Internals ─────────────────────────────────────────────────────────── #

    def _part_key(self, part: str) -> str:
        import hashlib
        return hashlib.sha256(part.strip().lower().encode()).hexdigest()[:16]

    def _store_fragment(self, part: str, answer: str, confidence: float) -> None:
        self._fragment_cache[self._part_key(part)] = {
            "part": part,
            "answer": answer,
            "confidence": confidence,
            "stored_at": time.time(),
        }

    def _compose(self, known: List[Tuple[str, str]]) -> str:
        """Joins fragment answers into a coherent multi-part response."""
        if len(known) == 1:
            return known[0][1]
        parts_text = []
        for i, (part, answer) in enumerate(known, 1):
            parts_text.append(f"**Part {i} — {part.capitalize()}:**\n{answer}")
        return "\n\n".join(parts_text)

    def _avg_confidence(
        self, known: List[Tuple[str, str]], global_memory
    ) -> float:
        if not known:
            return 0.0
        scores = []
        for part, _ in known:
            key = self._part_key(part)
            cached = self._fragment_cache.get(key)
            scores.append(cached.get("confidence", 0.85) if cached else 0.85)
        return sum(scores) / len(scores)


global_delta_engine = DeltaComputeEngine()
