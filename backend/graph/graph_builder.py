"""
Graph Builder — Constructs reasoning pattern graphs from successful inference runs.
Called after a full model inference to persist the reasoning for future reuse.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds and registers reasoning patterns into the GraphStore.
    Called post-inference to progressively improve the graph over time.
    """

    def __init__(self):
        from backend.graph.graph_store import global_graph_store
        self.store = global_graph_store

    def build_from_inference(
        self,
        normalized_query: Dict[str, Any],
        answer: str,
        steps: Optional[List[str]] = None,
        confidence: float = 0.9,
        tenant_id: str = "default",
    ):
        """
        Registers a new reasoning pattern if confidence is high enough.
        Only stores high-quality answers to avoid polluting the graph.
        """
        if confidence < 0.85:
            logger.debug(f"graph_skip: confidence={confidence:.2f} too low")
            return

        intent = normalized_query.get("intent", "general")
        entity = normalized_query.get("entity", "unknown")

        if intent == "general" and entity == "unknown":
            return  # Don't store non-specific queries

        # Derive pattern from reasoning steps or defaults
        if not steps:
            steps = self._derive_default_pattern(intent)

        self.store.store(
            intent=intent,
            entity=entity,
            pattern=steps,
            answer=answer,
            tenant_id=tenant_id,
        )
        logger.info(f"graph_built: intent={intent} entity={entity} steps={steps}")

    def _derive_default_pattern(self, intent: str) -> List[str]:
        """Maps intent to a default reasoning pattern."""
        patterns = {
            "definition":  ["retrieve", "summarize", "format"],
            "comparison":  ["retrieve_both", "contrast", "format"],
            "how_to":      ["retrieve", "sequence", "enumerate"],
            "calculation": ["parse", "compute", "format"],
            "summary":     ["retrieve", "compress", "format"],
            "explanation": ["retrieve", "reason", "format"],
        }
        return patterns.get(intent, ["retrieve", "reason", "format"])


global_graph_builder = GraphBuilder()
