"""
Enhancement Pipeline
The public entry point for the Answer Enhancement Engine.
Wraps the router and implements Chain-of-Enhancement (multi-pass).
"""
import logging
from typing import Tuple, List, Optional
from backend.enhancement.enhancement_router import EnhancementRouter

logger = logging.getLogger(__name__)

class EnhancementPipeline:
    """
    Manages the lifecycle of answer enhancement.
    Transforms HYPER into an AI Answer Reconstruction Engine.
    """

    def __init__(self):
        self.router = EnhancementRouter()

    def run(self, raw_answer: str, query: str, context_docs: Optional[List[str]] = None, intent: str = "general") -> Tuple[str, str]:
        """
        Runs the DLSS enhancement pipeline.
        Returns (Final_Answer, Status).
        Status is either "enhancement_success" or "fallback_required".
        """
        # Pass 1: Initial enhancement decision
        enhanced, status = self.router.process(raw_answer, query, context_docs, intent)

        if status == "enhanced" and enhanced:
            # BONUS: Chain-of-Enhancement (multi-pass formatting guarantee)
            # Run one final cleanup pass over the augmented text
            final_answer = self.router.enhancer.format(enhanced)
            logger.info(f"enhancement_success: query='{query[:30]}...' intent={intent}")
            return final_answer, "enhancement_success"

        logger.info(f"enhancement_bypassed: routing to fallback. query='{query[:30]}...'")
        return raw_answer, "fallback_required"

global_enhancement_pipeline = EnhancementPipeline()
