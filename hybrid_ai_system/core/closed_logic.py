import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ClosedSystem:
    """
    4. CLOSED SYSTEM (VERIFICATION ENGINE)
    - 5. ITERATION LOOP
    - feed error summary -> regenerate
    - retry until success or max_iter
    """
    def __init__(self, model_manager, verifier_engine):
        self.models = model_manager
        self.verifier = verifier_engine

    async def run_loop(self, task: str, constraints: str, tests: str, max_iter: int = 5) -> Optional[str]:
        error_signal = None
        
        for i in range(max_iter):
            logger.info(f"Closed Loop Iteration {i+1}")
            
            # Refine prompt with error signal
            error_context = f"\nPrevious Error: {error_signal}\nPlease fix this." if error_signal else ""
            prompt = f"Task: {task}\nConstraints: {constraints}{error_context}\nCode:\n```python\n"
            
            candidates = self.models.generate(prompt, k=3)
            
            for candidate in candidates:
                res = await self.verifier.verify_python(candidate, tests)
                if res["success"]:
                    logger.info("Verification Successful.")
                    return candidate
                
                error_signal = res["error_signal"]
                
        logger.error("Closed Loop failed to verify output.")
        return None
