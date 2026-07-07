from typing import List, Optional
from pydantic import BaseModel
from archive_engines.hyper_optimized_ai.config import settings

class AdaptiveResponse(BaseModel):
    content: str
    confidence: float
    assumptions: List[str] = []
    quick_fix: Optional[str] = None
    interpretations: List[str] = []
    needs_clarification: bool = False

class OutputControl:
    """
    6. OUTPUT CONTROL (ADAPTIVE)
    IF confidence >= 0.85: -> answer only
    IF 0.6-0.85: -> answer + 1 assumption + quick fix
    IF < 0.6: -> ask clarification OR provide 2 interpretations
    """
    
    def format_response(self, content: str, confidence: float, interpretations: List[str] = []) -> AdaptiveResponse:
        if confidence >= settings.ADAPTIVE_OUTPUT_HIGH_THRESHOLD:
            return AdaptiveResponse(content=content, confidence=confidence)
            
        elif confidence >= settings.ADAPTIVE_OUTPUT_MEDIUM_THRESHOLD:
            return AdaptiveResponse(
                content=content,
                confidence=confidence,
                assumptions=["The input refers to local CPU compute capabilities."],
                quick_fix="Adjust `compute_target` in your request to 'iGPU' if local CPU is too slow."
            )
            
        else:
            return AdaptiveResponse(
                content="I'm not confident enough to answer this directly.",
                confidence=confidence,
                interpretations=interpretations[:2],
                needs_clarification=True
            )

class SpeedLayer:
    """
    5. SPEED LAYER
    - Streaming output (instant first token)
    - Prefetch next likely query
    - Batch requests when possible
    """
    async def stream_response(self, generator):
        async for chunk in generator:
            yield chunk

    def prefetch_context(self, intent: str):
        # Prefetch related data from RAG or cache for the next likely query
        pass
