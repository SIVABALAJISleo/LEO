"""
backend/intelligence/micro_compute.py
Micro Compute Engine

Detects missing parts after composition and computes ONLY small missing sections
using a tiny CPU model (or fallback logic) instead of generating the full response.
"""
import logging
from typing import Optional
from backend.models.llm_loader import generate_response

logger = logging.getLogger(__name__)

class MicroComputeEngine:
    def execute(self, missing_concept: str, context: str = "") -> Optional[str]:
        """
        Runs a highly scoped query on the TinyLlama CPU model instead of
        escalating to the main heavy cluster.
        """
        logger.info(f"micro_compute: Generating tiny missing snippet for concept='{missing_concept}'")
        
        system_prompt = (
            "You are a specialized micro-service. Output ONLY a 1-2 sentence "
            "definition or explanation. Be extremely concise."
        )
        
        prompt = f"Define or explain: {missing_concept}"
        if context:
            prompt += f"\nContext: {context}"
            
        try:
            # We use our tiny CPU LLM loader
            result = generate_response(prompt, max_tokens=64, temperature=0.3, system_prompt=system_prompt)
            logger.info("micro_compute: Successfully computed micro-section.")
            return result
        except Exception as e:
            logger.error(f"micro_compute: Failed - {e}")
            return None

global_micro_compute = MicroComputeEngine()
