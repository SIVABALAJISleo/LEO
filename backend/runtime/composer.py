"""
backend/runtime/composer.py
Runtime Composition-Only Response Engine (Upgraded).

Assembles responses from precomputed fragments stored in the Knowledge Graph.
Strictly NO new LLM generation allowed here.
"""
import logging
from typing import Dict, Any, Optional
from backend.normalization.normalizer import global_normalizer
from backend.graph.fragment_graph import global_fragment_graph
from backend.answers.fragment_engine import global_fragment_composer
from backend.analytics.metrics import global_metrics

logger = logging.getLogger(__name__)

class RuntimeComposer:
    def compose_response(self, query: str, context: Dict[str, Any], context_fragments: list) -> tuple[Optional[str], list[str]]:
        """
        Dynamically assembles an answer from the Fragment Graph.
        Point 5 & 6 & 10: Composition with Decomposition and Context Adaptation.
        """
        components = context.get("components", [query])
        user_context = context.get("user_context", "default") # Point 10
        
        logger.info(f"runtime_composer: Composing from {len(components)} components for context '{user_context}'")
        
        final_answer_parts = []
        missing_components = []
        
        for part in components:
            norm = global_normalizer.normalize(part)
            entity = norm["entity"]
            
            # 1. Fetch fragments from the Graph (Point 6 Mapping)
            fragments = global_fragment_graph.get_fragments(entity)
            if not fragments:
                 # Try intent mapping if entity fails
                 fragments = global_fragment_graph.get_fragments(norm["intent"].upper())
                 
            if fragments:
                # 2. Context Adaptation (Point 10): Select style based on user_context
                # In this system, we filter or prioritize fragments based on style tags
                style = self._get_target_style(user_context)
                
                # Assembly using FragmentComposer
                composition = global_fragment_composer.compose(fragments) # Can be extended for style
                if composition:
                    final_answer_parts.append(composition)
                else:
                    missing_components.append(part)
            else:
                missing_components.append(part)

        if final_answer_parts:
            # Join multiple component answers (Point 6 Composition)
            full_composition = "\n\n".join(final_answer_parts)
            logger.info(f"runtime_composer: Assembled answer from {len(final_answer_parts)} parts. Missing: {len(missing_components)}")
            return full_composition, missing_components

        return None, components

    def _get_target_style(self, user_context: str) -> str:
        """Point 10: Select style based on user context."""
        if "pro" in user_context.lower():
            return "technical"
        elif "quick" in user_context.lower():
            return "concise"
        return "balanced"

global_runtime_composer = RuntimeComposer()
