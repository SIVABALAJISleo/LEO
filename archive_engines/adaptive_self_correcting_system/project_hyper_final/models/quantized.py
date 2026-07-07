import asyncio
from typing import AsyncGenerator

class ModelLayer:
    """
    LAYER 5: MODEL LAYER (CPU ONLY)
    Quantized GGUF / speculative decoding simulation.
    """
    async def stream_tiny(self, query: str) -> AsyncGenerator[str, None]:
        # Quantized INT4 Fast Path
        for token in ["Fast ", "path ", "CPU ", "output ", "complete."]:
            await asyncio.sleep(0.02)
            yield token

    async def stream_medium(self, query: str, context: str) -> AsyncGenerator[str, None]:
        # 7B Speculative Decoding simulation
        for token in ["Reasoned ", "output ", "using ", "context: ", context[:20], "..."]:
            await asyncio.sleep(0.05)
            yield token

model_layer = ModelLayer()

