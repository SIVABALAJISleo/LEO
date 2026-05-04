import asyncio
from typing import AsyncGenerator
from .schemas.contracts import QueryRequest, ComplexityLevel
from .router.adaptive_router import adaptive_router
from .cache.semantic_cache import semantic_cache
from .rag.hierarchical_rag import hierarchical_rag
from .models.inference import inference_engine
import numpy as np

class LeoOrchestrator:
    """
    MASTER ORCHESTRATOR
    Wires all layers into a single streaming execution flow.
    """
    async def stream_response(self, request: QueryRequest) -> AsyncGenerator[str, None]:
        query = request.query
        
        # 1. Routing
        path = adaptive_router.route(query, request.latency_budget_ms)
        
        # 2. Layer 0: Cache Check (Fuzzy)
        mock_embedding = np.random.rand(128) # Simulated sentence embedding
        cached = semantic_cache.lookup(mock_embedding)
        if cached:
            yield f"[CACHE_HIT] {cached['answer']}"
            return

        # 3. Execution Paths
        if path == "PATH_CACHE_TINY":
            async for token in inference_engine.stream_tiny(query):
                yield token
        
        elif path == "PATH_RAG_QUANTIZED":
            chunks = hierarchical_rag.retrieve(query)
            context = hierarchical_rag.build_context(chunks)
            async for token in inference_engine.stream_medium(query, context):
                yield token
                
        else: # PATH_ASYNC_HEAVY
            yield "[ASYNC_HEAVY_INITIAL] Your request is complex. Processing in background..."
            # (Queue logic would be triggered here)

leo_orchestrator = LeoOrchestrator()
吐
