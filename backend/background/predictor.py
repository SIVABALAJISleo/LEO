"""
backend/background/predictor.py
Predictive Query Expansion Module.

Generates variations and follow-up questions for proactive precomputation.
"""
import logging
from typing import List
from backend.models.llm_loader import generate_response

logger = logging.getLogger(__name__)

class QueryPredictor:
    async def predict_variations(self, query: str) -> List[str]:
        """
        Generates 15-20 variations of the query for proactive precomputation.
        This maximizes future cache hit rates for Zero-Runtime Compute.
        """
        logger.info(f"bg_predictor: Predicting 20 variations for '{query}'")
        
        system_prompt = (
            "You are a predictive query engine. Output ONLY a comma-separated list "
            "of 20 likely follow-up questions or semantic variations. No numbering or explanations."
        )
        
        prompt = f"Given the query: '{query}', predict the next 20 most relevant questions or variations."
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, generate_response, prompt, 512, 0.7, system_prompt
            )
            
            # Parsing: split by common delimiters
            variations = []
            for line in result.replace('\n', ',').split(','):
                v = line.strip()
                if v and len(v) > 5:
                    # Clean up some common LLM artifacts
                    v = v.lstrip('1234567890. ')
                    variations.append(v)
                    
            logger.info(f"bg_predictor: Generated {len(variations)} variations.")
            return variations[:20]
            
        except Exception as e:
            logger.error(f"bg_predictor: Prediction failed - {e}")
            return []

global_predictor = QueryPredictor()
