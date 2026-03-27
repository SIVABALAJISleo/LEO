"""
backend/runtime/composer.py
Runtime Composition-Only Response Engine.

Assembles responses from precomputed fragments, stored answers, and templates.
Strictly NO new LLM generation allowed here.
"""
import logging
from typing import Dict, Any, Optional
from backend.intelligence.decomposer import global_decomposer
from backend.intelligence.composer_engine import global_composer_engine
from backend.intelligence.creative_engine import global_creative_engine
from backend.intelligence.confidence_gate import global_confidence_gate_v2
from backend.analytics.metrics import global_metrics
from backend.intelligence.delta_engine import _extract_intent_parts

logger = logging.getLogger(__name__)

class RuntimeComposer:
    def compose_response(self, query: str, decomposed: Dict[str, Any], context_fragments: list) -> Optional[str]:
        """
        Attempts to build a complete response using structured fragments:
        Definition, Steps, Examples, Advantages.
        """
        logger.info(f"runtime_composer: Structured composition for '{query}'")
        
        # 1. Map fragments to types (Definition, Steps, etc.)
        intents = _extract_intent_parts(query)
        
        # 2. Try factual composition with structured priority
        composition = ""
        found_fact = False
        
        if "definition" in intents:
             comp = global_composer_engine.compose({"definition": decomposed.get("topic")})
             if comp:
                  composition += f"Definition: {comp}\n\n"
                  found_fact = True
                  
        if "steps" in intents:
             comp = global_composer_engine.compose({"steps": decomposed.get("topic")})
             if comp:
                  composition += f"Steps:\n{comp}\n\n"
                  found_fact = True

        # Fallback to general composition if specialized fails
        if not found_fact:
             composition = global_composer_engine.compose(decomposed)
        
        # 3. If it's creative, try simulation
        if not composition and decomposed.get("is_creative"):
             composition = global_creative_engine.simulate(decomposed, context_fragments)

        if not composition:
            return None

        # 4. Final confidence check
        confidence = global_confidence_gate_v2.evaluate(composition, query, decomposed)
        if confidence >= 0.75: # Lowered threshold (Phase 30)
            return composition

        return None

global_runtime_composer = RuntimeComposer()
