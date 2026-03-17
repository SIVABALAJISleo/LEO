"""
Answer Graph Engine (AGE)
Core engine that matches new queries to stored reasoning patterns
and returns reused answers without model calls.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AnswerGraphEngine:
    """
    Matches normalized queries to stored reasoning graphs.
    Returns a reused answer if a matching pattern is found.
    This is the highest-priority bypass layer — checked before everything else.
    """

    def __init__(self):
        from backend.graph.graph_store import global_graph_store
        self.store = global_graph_store

    def lookup(self, normalized_query: Dict[str, Any], tenant_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Attempts to find a reusable answer from the graph.
        Returns a result dict or None if no match.
        """
        intent = normalized_query.get("intent")
        entity = normalized_query.get("entity")

        if not intent or not entity:
            return None

        graph_entry = self.store.lookup(intent, entity, tenant_id)

        if graph_entry:
            logger.info(f"age_hit: intent={intent} entity={entity}")
            return {
                "answer": graph_entry["answer"],
                "mode": "ANSWER_GRAPH",
                "confidence": 0.92,
                "pattern": graph_entry.get("pattern", []),
                "graph_hits": graph_entry.get("hits", 0),
            }

        return None

    def register_answer(
        self,
        normalized_query: Dict[str, Any],
        answer: str,
        confidence: float,
        steps=None,
        tenant_id: str = "default",
    ):
        """
        Registers a new answer into the graph for future reuse.
        Called from the orchestrator post-inference.
        """
        from backend.graph.graph_builder import global_graph_builder
        global_graph_builder.build_from_inference(
            normalized_query=normalized_query,
            answer=answer,
            steps=steps,
            confidence=confidence,
            tenant_id=tenant_id,
        )


global_age = AnswerGraphEngine()
