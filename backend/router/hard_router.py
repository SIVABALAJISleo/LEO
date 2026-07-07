"""
Hard Routing Engine
STRICT ordered pipeline router — no exceptions, no random execution.
Priority: precomputed → canonical → template → graph → retrieval → model

This is the EXECUTION CONTROLLER for the entire pipeline.
"""
import logging
from typing import Dict, Any, Callable, List

logger = logging.getLogger(__name__)

# Pipeline stages in STRICT priority order
PIPELINE_STAGES = [
    "canonical",       # 1. Canonical answer store — one answer per concept
    "precomputed",     # 2. PPE / shadow store hits
    "template",        # 3. Template compiler (zero cost)
    "graph",           # 4. Answer graph engine (reasoning reuse)
    "reasoning_mem",   # 5. Reasoning memory (step reuse)
    "semantic_cache",  # 6. Semantic cache
    "retrieval",       # 7. RAG retrieval (confidence gated)
    "enhancement",     # 8. Answer enhancement (no large model)
    "micro_model",     # 9. Micro / specialized model
    "large_model",     # 10. Large model — LAST RESORT ONLY
]

RETRIEVAL_CONFIDENCE_THRESHOLD = 0.90  # Must exceed to accept retrieval


class HardRouter:
    """
    Strict ordered pipeline executor.
    Each stage is attempted in order; if it returns a result above confidence threshold, stop.
    Model is only invoked if ALL preceding stages fail.
    """

    def route(
        self,
        shaped_query: Dict[str, Any],
        stage_handlers: Dict[str, Callable],
        confidence_gate,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Executes pipeline stages in strict order.
        stage_handlers: {stage_name: callable(shaped_query) -> Optional[str]}
        """
        entity = shaped_query.get("entity", "?")
        intent = shaped_query.get("intent", "?")
        attempted: List[str] = []

        for stage in PIPELINE_STAGES:
            handler = stage_handlers.get(stage)
            if not handler:
                continue

            try:
                result = handler(shaped_query)
            except Exception as e:
                logger.warning(f"hard_router_stage_error: stage={stage} error={e}")
                result = None

            if result:
                answer = result if isinstance(result, str) else result.get("answer", "")
                if answer:
                    attempted.append(stage)
                    # Confidence gate check
                    conf = confidence_gate.quick_score_source(stage.upper())
                    if stage == "retrieval" and conf < RETRIEVAL_CONFIDENCE_THRESHOLD:
                        logger.debug(f"hard_router_skip: stage=retrieval confidence={conf:.2f}")
                        continue

                    logger.info(f"hard_router_hit: stage={stage} entity={entity} intent={intent}")
                    return {
                        "answer": answer,
                        "mode": stage.upper(),
                        "confidence": conf,
                        "pipeline_stages_attempted": attempted,
                        "model_used": stage == "large_model",
                    }

        # Should NEVER reach here in a well-configured system
        logger.error(f"hard_router_exhausted: all stages failed for entity={entity}")
        return {
            "answer": f"Unable to answer '{entity}' query at this time.",
            "mode": "EXHAUSTED",
            "confidence": 0.0,
            "pipeline_stages_attempted": attempted,
            "model_used": False,
        }

    def get_model_bypass_rate(self, history: List[Dict]) -> float:
        """Calculate % of requests that avoided large model."""
        if not history:
            return 0.0
        bypassed = sum(1 for h in history if not h.get("model_used", True))
        return bypassed / len(history)


global_hard_router = HardRouter()
