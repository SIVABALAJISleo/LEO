"""
backend/predictive/massive_prediction_engine.py

Massive Prediction Engine
==========================
For EACH incoming query, generates 20–50 variations + follow-ups,
precomputes them in background, stores permanently.

Rules:
  - Zero repeat: everything computed gets stored
  - Background only: never blocks the response path
  - Coverage: 50+ semantic permutations per query family
"""
import logging
import asyncio
from typing import Dict, List, Any, Set

logger = logging.getLogger(__name__)

# ── Base templates for variation explosion ────────────────────────────────────
DEFINITION_TEMPLATES: List[str] = [
    "What is {entity}?",
    "Define {entity}",
    "Explain {entity}",
    "Describe {entity}",
    "What does {entity} mean?",
    "Give me the meaning of {entity}",
    "What exactly is {entity}?",
    "Can you explain {entity}?",
    "Tell me about {entity}",
    "Overview of {entity}",
    "{entity} definition",
    "Simple explanation of {entity}",
    "I don't understand {entity}, help me",
]

HOW_TO_TEMPLATES: List[str] = [
    "How does {entity} work?",
    "How to use {entity}?",
    "How to implement {entity}?",
    "How can I use {entity}?",
    "How to get started with {entity}?",
    "Guide to {entity}",
    "Tutorial for {entity}",
    "Steps to use {entity}",
    "How to configure {entity}?",
    "How to optimize {entity}?",
]

COMPARISON_TEMPLATES: List[str] = [
    "{entity} vs alternatives",
    "When to use {entity}?",
    "{entity} pros and cons",
    "Advantages of {entity}",
    "Disadvantages of {entity}",
    "Is {entity} good?",
    "{entity} performance comparison",
]

FOLLOW_UP_TEMPLATES: List[str] = [
    "Best practices for {entity}",
    "Common mistakes with {entity}",
    "Troubleshoot {entity} issues",
    "Scale {entity} in production",
    "Optimize {entity} performance",
    "{entity} in real world",
    "Advanced {entity} techniques",
    "Cost of using {entity}",
    "Security considerations for {entity}",
    "{entity} community resources",
    "Alternatives to {entity}",
    "{entity} use cases",
]

ALL_TEMPLATES = (
    DEFINITION_TEMPLATES
    + HOW_TO_TEMPLATES
    + COMPARISON_TEMPLATES
    + FOLLOW_UP_TEMPLATES
)  # 42 templates → guaranteed ≥20 after deduplication


class MassivePredictionEngine:
    """
    Generates 20–50+ unique query variations per entity/intent,
    then enqueues ALL of them for background precompute.
    Every result is permanently stored → zero future compute.
    """

    def __init__(self):
        # Track which family_ids have been expanded (avoid re-expansion)
        self._expanded_families: Set[str] = set()

    # ── Variation Generation ───────────────────────────────────────────────── #

    def generate_variations(
        self,
        query: str,
        entity: str,
        intent: str,
        family_id: str,
    ) -> Dict[str, Any]:
        """
        Produces 20–50 variations + follow-ups for the given entity.
        Returns: {"variations": [...], "follow_ups": [...]}
        """
        entity_clean = entity.lower().replace("_", " ")

        # Render all templates
        seen: Set[str] = {query.lower().strip()}
        variations: List[str] = []
        follow_ups: List[str] = []

        for tmpl in DEFINITION_TEMPLATES + HOW_TO_TEMPLATES + COMPARISON_TEMPLATES:
            rendered = tmpl.format(entity=entity_clean)
            if rendered.lower() not in seen:
                variations.append(rendered)
                seen.add(rendered.lower())

        for tmpl in FOLLOW_UP_TEMPLATES:
            rendered = tmpl.format(entity=entity_clean)
            if rendered.lower() not in seen:
                follow_ups.append(rendered)
                seen.add(rendered.lower())

        # Intent-specific extras
        intent_extras = self._intent_extras(entity_clean, intent, seen)
        variations.extend(intent_extras)

        logger.debug(
            f"massive_pred: family={family_id} "
            f"variations={len(variations)} follow_ups={len(follow_ups)}"
        )
        return {
            "variations": variations[:30],   # cap at 30 base variations
            "follow_ups": follow_ups[:20],   # cap at 20 follow-ups
            "total": len(variations) + len(follow_ups),
        }

    # ── Background Precompute ─────────────────────────────────────────────── #

    async def precompute_family(
        self,
        query: str,
        entity: str,
        intent: str,
        family_id: str,
        tenant_id: str,
        session_id: str,
    ) -> None:
        """
        Fire-and-forget: enqueues all variations for background compute.
        If family already expanded, skips (zero-repeat guarantee).
        """
        if family_id in self._expanded_families:
            logger.debug(f"massive_pred.skip: family={family_id} already expanded")
            return

        self._expanded_families.add(family_id)

        preds = self.generate_variations(query, entity, intent, family_id)
        all_queries = preds["variations"] + preds["follow_ups"]

        try:
            from backend.background.compute_engine import global_bg_compute
            for q in all_queries:
                asyncio.create_task(
                    global_bg_compute.enqueue(
                        q, tenant_id, "SYSTEM", session_id, priority="predicted"
                    )
                )
            logger.info(
                f"massive_pred.enqueued: family={family_id} "
                f"queries={len(all_queries)} tenant={tenant_id}"
            )
        except Exception as exc:
            logger.warning(f"massive_pred.enqueue_error: {exc}")

    # ── Internal helpers ──────────────────────────────────────────────────── #

    def _intent_extras(
        self, entity: str, intent: str, seen: Set[str]
    ) -> List[str]:
        extras: List[str] = []
        candidates: Dict[str, List[str]] = {
            "definition":  [f"What is meant by {entity}?", f"Short summary of {entity}"],
            "how_to":      [f"Quickstart for {entity}", f"Step by step {entity} guide"],
            "comparison":  [f"Difference between {entity} and RAG", f"{entity} benchmark"],
            "troubleshoot":[f"Why is {entity} failing?", f"Common {entity} bugs"],
            "benefit":     [f"Why should I use {entity}?", f"Value of {entity}"],
            "calculation": [f"{entity} formula", f"How to compute {entity}?"],
        }
        for q in candidates.get(intent, []):
            if q.lower() not in seen:
                extras.append(q)
                seen.add(q.lower())
        return extras

    def stats(self) -> Dict[str, Any]:
        return {"expanded_families": len(self._expanded_families)}


global_massive_predictor = MassivePredictionEngine()
