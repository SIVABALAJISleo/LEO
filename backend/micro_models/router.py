import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MicroModelRouter:
    """
    Routes specialized intents (math, code, summary) to tiny, optimized models.
    Avoids escalating to large models for simple specialized tasks.
    """
    def __init__(self):
        # In a real system, these would be local llama-cpp or onnx models
        self.specialties = {
            "math": "MathBERT-Tiny",
            "code": "CodeLlama-1b-Int8",
            "summarization": "BART-Base-Distilled",
            "classification": "BERT-Tiny"
        }

    def route(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        if any(w in query_lower for w in ["calculate", "math", "+", "-", "*", "/", "="]):
            return "math"
        if any(w in query_lower for w in ["summarize", "tl;dr", "shorten"]):
            return "summarization"
        if any(w in query_lower for w in ["python", "javascript", "code", "function", "class"]):
            return "code"
        return None

    async def execute(self, query: str, specialty: str) -> str:
        model_name = self.specialties.get(specialty)
        logger.info(f"micro_model_execution: type={specialty} model={model_name}")
        
        # Use LocalInference for real CPU-first execution
        from rag.inference import LocalInference
        # We use a dedicated threads count for micro-models to keep them ultra-fast
        inference = LocalInference() 
        
        # Specialized prompting for micro-tasks
        prompt = f"<|system|>\nYou are a specialized {specialty} assistant. Output ONLY the result.\n<|user|>\n{query}\n<|assistant|>\n"
        
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            inference.generate, 
            prompt, 
            128 # Micro-models use fewer tokens for speed
        )
        return str(result)

global_micro_router = MicroModelRouter()
