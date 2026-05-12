"""
backend/router/triattention_router.py

TriAttention Router — STRICT 3-tier ordered routing:
  1. Exact cache (family_id match)  → <10ms
  2. Semantic match (>=0.88, top_k=3) → <50ms
  3. Prediction match               → <50ms

Rules:
  - ANY hit → return instantly
  - Confidence MUST be >= 0.95 before returning cached answer
  - If confidence < 0.95 → escalate to compute
  - NEVER returns an uncertain cached result
"""
import logging
import time
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# Thresholds — STRICT per spec
SEMANTIC_THRESHOLD = 0.88    # minimum cosine similarity for tier 2
CONFIDENCE_FLOOR   = 0.95    # minimum confidence to RETURN cached answer
TOP_K              = 3       # top-k candidates evaluated in semantic search


class TriAttentionRouter:
    """
    Executes 3-tier ordered lookup in strict priority.
    Returns (result, tier_name) or (None, None) if all tiers miss.
    """

    # ------------------------------------------------------------------ #
    # TIER 1 — Exact Family Match                                          #
    # ------------------------------------------------------------------ #
    def tier1_exact(
        self,
        family_id: str,
        shadow_store,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Exact lookup via family_id → shadow/canonical store.
        Confidence must be >= CONFIDENCE_FLOOR; otherwise reject.
        """
        try:
            result = shadow_store.lookup(family_id, session_id)
            if result is None:
                return None

            conf = result.get("confidence", 0.0)
            if conf < CONFIDENCE_FLOOR:
                logger.debug(
                    f"triattention.tier1_reject: family={family_id} "
                    f"confidence={conf:.3f} < {CONFIDENCE_FLOOR}"
                )
                return None  # ← NEVER return uncertain result (spec rule)

            logger.info(
                f"triattention.tier1_hit: family={family_id} "
                f"confidence={conf:.3f}"
            )
            return {**result, "tier": "exact_cache", "tier_index": 1}
        except Exception as exc:
            logger.warning(f"triattention.tier1_error: {exc}")
            return None

    # ------------------------------------------------------------------ #
    # TIER 2 — Semantic Match (≥0.88, top_k=3)                           #
    # ------------------------------------------------------------------ #
    def tier2_semantic(
        self,
        query: str,
        global_memory,
        threshold: float = SEMANTIC_THRESHOLD,
    ) -> Optional[Dict[str, Any]]:
        """
        Searches FAISS index for top_k neighbours; accepts if similarity ≥ threshold.
        Confidence gated at CONFIDENCE_FLOOR before return.
        """
        try:
            hits: List[Dict[str, Any]] = global_memory.search(
                query, k=TOP_K, threshold=threshold
            )
            if not hits:
                return None

            # Best candidate
            best = hits[0]
            conf = best.get("confidence", 0.0)

            if conf < CONFIDENCE_FLOOR:
                logger.debug(
                    f"triattention.tier2_reject: similarity_ok but "
                    f"confidence={conf:.3f} < {CONFIDENCE_FLOOR}"
                )
                return None

            logger.info(
                f"triattention.tier2_hit: similarity={best.get('similarity', 0):.3f} "
                f"confidence={conf:.3f} top_k={len(hits)}"
            )
            return {**best, "tier": "semantic_match", "tier_index": 2}
        except Exception as exc:
            logger.warning(f"triattention.tier2_error: {exc}")
            return None

    # ------------------------------------------------------------------ #
    # TIER 3 — Prediction Match                                           #
    # ------------------------------------------------------------------ #
    def tier3_prediction(
        self,
        query: str,
        session_id: str,
        predictor,
        global_memory,
    ) -> Optional[Dict[str, Any]]:
        """
        Uses predictor to generate variations/follow-ups, then checks each
        against global_memory. Only returns if confidence >= CONFIDENCE_FLOOR.
        """
        try:
            preds = predictor.predict_next_queries(query, session_id)
            candidates = preds.get("variations", []) + preds.get("follow_ups", [])

            for candidate in candidates[:30]:  # limit search space
                hit = global_memory.lookup(candidate)
                if hit is None:
                    continue
                conf = hit.get("confidence", 0.0)
                if conf >= CONFIDENCE_FLOOR:
                    logger.info(
                        f"triattention.tier3_hit: candidate='{candidate}' "
                        f"confidence={conf:.3f}"
                    )
                    return {**hit, "tier": "prediction_match", "tier_index": 3}

            return None
        except Exception as exc:
            logger.warning(f"triattention.tier3_error: {exc}")
            return None

    # ------------------------------------------------------------------ #
    # Main Entry — route() — STRICT execution order                       #
    # ------------------------------------------------------------------ #
    def route(
        self,
        query: str,
        family_id: str,
        session_id: str,
        shadow_store,
        global_memory,
        predictor,
        semantic_threshold: float = SEMANTIC_THRESHOLD,
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Executes tiers in strict order. Returns on first hit.
        Returns: (result_dict | None, tier_name | "miss")
        """
        t0 = time.monotonic()

        # TIER 1
        hit = self.tier1_exact(family_id, shadow_store, session_id)
        if hit:
            hit["triattention_latency_ms"] = (time.monotonic() - t0) * 1000
            return hit, "tier1_exact"

        # TIER 2
        hit = self.tier2_semantic(query, global_memory, threshold=semantic_threshold)
        if hit:
            hit["triattention_latency_ms"] = (time.monotonic() - t0) * 1000
            return hit, "tier2_semantic"

        # TIER 3
        hit = self.tier3_prediction(query, session_id, predictor, global_memory)
        if hit:
            hit["triattention_latency_ms"] = (time.monotonic() - t0) * 1000
            return hit, "tier3_prediction"

        total_ms = (time.monotonic() - t0) * 1000
        logger.debug(f"triattention.miss: family={family_id} elapsed={total_ms:.1f}ms")
        return None, "miss"


global_triattention_router = TriAttentionRouter()
