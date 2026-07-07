from typing import AsyncGenerator
import numpy as np
from .router.brain import brain, ComplexityLevel
from .cache.fuzzy import fuzzy_cache
from .rag.engine import rag_engine
from .models.quantized import model_layer
from .fallback.controller import fallback_system
from .schemas.contracts import QueryRequest

class HYPEROrchestrator:
    """
    MASTER ORCHESTRATOR
    Coordinates the multi-tier execution and fallback loops.
    """
    async def process(self, request: QueryRequest) -> AsyncGenerator[str, None]:
        query = request.query
        
        # 1. Routing & Analysis
        path = brain.route(query)
        
        # 2. Semantic Cache (Fuzzy)
        mock_embedding = np.random.rand(128) # Simulated embedding
        cached = fuzzy_cache.lookup(mock_embedding)
        if cached:
            yield f"[CACHE_HIT] {cached['response']}"
            return

        # 3. Execution Paths
        if path == "PATH_CACHE_TINY":
            async for token in model_layer.stream_tiny(query):
                yield token
        
        elif path == "PATH_RAG_MEDIUM":
            contexts = rag_engine.retrieve(query)
            refined_contexts = rag_engine.rerank(query, contexts)
            context_str = refined_contexts[0]
            async for token in model_layer.stream_medium(query, context_str):
                yield token

        elif path == "PATH_FALLBACK_ANYTIME":
            # [CRITICAL] 1% Control System
            result = fallback_system.trigger(ComplexityLevel.EXTREME)
            yield f"[FALLBACK_ACTIVE] {result['answer']}"
            
        else: # PATH_HEAVY_ASYNC
            yield "[ASYNC_HEAVY] Processing complex intent in background..."

orchestrator = HYPEROrchestrator()

