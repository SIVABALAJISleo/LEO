"""
backend/intelligence/confidence_gate.py
Confidence Gating System

Evaluates the composed/simulated answer quality.
Determines if we can return early, trigger micro-compute, or fallback to the heavy LLM.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfidenceGate:
    def __init__(self, threshold_high: float = 0.85, threshold_low: float = 0.5):
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        
    def evaluate(self, composition: str, query: str, decomposed: Dict[str, Any]) -> float:
        """
        Heuristic confidence evaluation.
        """
        if not composition or len(composition) < 20:
            return 0.0
            
        score = 0.5
        
        # Does the composition actually contain the entities we detected?
        entities = decomposed.get("entities", [])
        comp_lower = composition.lower()
        matched_entities = sum(1 for e in entities if e.lower() in comp_lower)
        
        if entities:
            score += 0.3 * (matched_entities / len(entities))
            
        # Is the text reasonably structured?
        if "\n" in composition or "." in composition:
            score += 0.1
            
        # Does it actually address the intent?
        intent = decomposed.get("intent", "information")
        if intent == "how_to" and ("1." in composition or "step" in comp_lower):
            score += 0.1
        elif intent == "example" and ("example" in comp_lower or "instance" in comp_lower):
            score += 0.1
            
        final_score = min(1.0, max(0.0, score))
        logger.info(f"confidence_gate: Evaluated composition at confidence={final_score:.2f}")
        return final_score

global_confidence_gate_v2 = ConfidenceGate()
