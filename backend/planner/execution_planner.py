"""
Execution Planner
Decides the optimal processing path for each query based on normalization results.
Implements the HYPER priority ordering:
  reuse > template > retrieval > enhancement > micro_model > model
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Pipeline layers in priority order
PIPELINE_LAYERS = [
    "answer_graph",      # Layer 1: Reuse stored reasoning
    "predictive_store",  # Layer 2: Pre-computed answers
    "shadow_store",      # Layer 3: Shadow execution cache
    "semantic_cache",    # Layer 4: Semantic similarity cache
    "template",          # Layer 5: Template compiler
    "knowledge_graph",   # Layer 6: Knowledge graph lookup
    "retrieval",         # Layer 7: RAG retrieval
    "enhancement",       # Layer 8: Answer enhancement
    "micro_model",       # Layer 9: Specialized micro model
    "model_ladder",      # Layer 10: Full model (last resort)
]

# Simple queries skip to template/retrieval; complex queries may go straight to model
COMPLEXITY_SKIP_MAP = {
    "simple":  ["answer_graph", "template", "retrieval"],
    "medium":  ["answer_graph", "predictive_store", "shadow_store", "semantic_cache", "template", "retrieval", "enhancement"],
    "complex": PIPELINE_LAYERS,  # All layers
}


class ExecutionPlanner:
    """
    Determines the most efficient execution path for a given query.
    Returns an ordered list of layers to attempt.
    """

    def plan(self, normalized_query: Dict[str, Any]) -> List[str]:
        """
        Returns an ordered list of pipeline layers to try.
        """
        complexity = normalized_query.get("complexity", "medium")
        plan = COMPLEXITY_SKIP_MAP.get(complexity, PIPELINE_LAYERS)
        logger.debug(f"execution_plan: complexity={complexity} layers={plan}")
        return plan

    def describe_plan(self, plan: List[str]) -> str:
        """Human-readable plan description for telemetry."""
        return " → ".join(plan)

    def is_model_required(self, completed_layers: List[str], answer: str) -> bool:
        """
        Returns True only if no bypass layer found an answer.
        """
        model_free_layers = set(PIPELINE_LAYERS) - {"micro_model", "model_ladder"}
        return not any(layer in completed_layers for layer in model_free_layers) or not answer


global_execution_planner = ExecutionPlanner()
