"""
backend/optimization/rephraser.py
Lightweight Rephraser for Zero Runtime Compute.

Adapts existing answers to new query phrasing using rule-based logic.
"""
import logging

logger = logging.getLogger(__name__)

class LightweightRephraser:
    def rephrase(self, answer: str, original_query: str, new_query: str) -> str:
        """
        Adapts the answer to better fit the new query context without LLM.
        In this implementation, it performs simple string normalization.
        """
        logger.info(f"rephraser: Adapting answer for new phrasing.")
        
        # Rule-based adaptation (Simplified)
        # If the user asks for 'examples' and the answer has them, we highlight them.
        if "example" in new_query.lower() and "example" not in answer.lower():
            # This is where we might append a template or fragment
            pass
            
        return answer

global_rephraser = LightweightRephraser()
