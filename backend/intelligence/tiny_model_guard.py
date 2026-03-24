import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TinyModelGuard:
    """
    First line of defense. Runs a sub-1B model (via llama.cpp or ONNX)
    and evaluates if the response is 'good enough' to avoid escalation.
    """
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    async def evaluate(self, query: str, model_manager: Any, context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Executes a tiny model and checks confidence.
        If confidence > threshold, returns the answer.
        """
        try:
            # Request tiny_model tier
            result = await model_manager.generate_safe(
                query, 
                context=context, 
                tier="tiny",
                max_tokens=256
            )
            
            confidence = float(result.get("confidence", 0.5))
            logger.info(f"tiny_model_eval: query={query[:30]}... conf={confidence}")
            
            if confidence >= self.threshold:
                return {
                    "answer": result["answer"],
                    "confidence": confidence,
                    "mode": "TINY_MODEL",
                    "expert": "tiny_guard"
                }
        except Exception as e:
            logger.warning(f"tiny_model_failed: {e}")
            
        return None

global_tiny_guard = TinyModelGuard()
