import time
import numpy as np
from .cache_rag import SemanticCacheLayer, RagLayer
from .models_router import AdaptiveComputeRouter, TinyModelLayer, MediumModelLayer, HeavyModelLayer
from ..models.schemas import CascadeResponse, CascadeLayer, CascadeStatus

class CascadeOrchestrator:
    """THE MASTER CASCADE PIPELINE"""
    def __init__(self, confidence_floor: float = 0.90):
        self.cache = SemanticCacheLayer()
        self.rag = RagLayer()
        self.router = AdaptiveComputeRouter()
        self.tiny = TinyModelLayer()
        self.medium = MediumModelLayer()
        self.heavy = HeavyModelLayer()
        self.confidence_floor = confidence_floor

    async def run(self, query: str) -> CascadeResponse:
        start_time = time.time()
        
        # [LAYER 0] SEMANTIC CACHE
        mock_embedding = np.random.rand(128) # Simulated embedding
        cached = self.cache.check(mock_embedding)
        if cached:
            return self._response(cached, CascadeLayer.CACHE, 1.0, start_time, CascadeStatus.SUCCESS, 0.0)

        # [LAYER 1] RAG
        self.rag.retrieve(query)
        
        # [ROUTING] COMPLEXITY ESTIMATION
        complexity = self.router.estimate_complexity(query)
        
        # [LAYER 2] TINY MODEL
        if complexity == "SIMPLE":
            ans, conf = await self.tiny.infer(query)
            if conf >= self.confidence_floor:
                return self._response(ans, CascadeLayer.TINY, conf, start_time, CascadeStatus.SUCCESS, 0.1)

        # [LAYER 3] MEDIUM MODEL
        ans, conf = await self.medium.infer(query)
        if conf >= self.confidence_floor:
            return self._response(ans, CascadeLayer.MEDIUM, conf, start_time, CascadeStatus.SUCCESS, 0.4)

        # [LAYER 4] HEAVY COMPUTE (Last Resort)
        ans = await self.heavy.infer(query)
        return self._response(ans, CascadeLayer.HEAVY, 0.99, start_time, CascadeStatus.SUCCESS, 1.0)

    def _response(self, ans, layer, conf, start, status, cost):
        return CascadeResponse(
            answer=ans,
            layer_handled=layer,
            confidence=conf,
            latency_ms=(time.time() - start) * 1000,
            status=status,
            compute_cost_score=cost
        )

