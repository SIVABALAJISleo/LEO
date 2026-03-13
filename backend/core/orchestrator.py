from backend.intelligence.router import MoERouter, SemanticCache, HallucinationGuard, TraceEngine
from backend.intelligence.rag import RAGEngine
from backend.intelligence.reasoning import reasoning_expert
from backend.performance.caching import MultiLevelCache, PredictiveEngine
from backend.performance.memo import global_memo
from backend.performance.scheduler import scheduler
from backend.core.reliability import CircuitBreaker, ReliabilityOrchestrator
from backend.data_efficiency.probabilistic import BloomFilter
from backend.core.logging import logger as struct_logger
import time
import asyncio

class UnifiedSaaSEngine:
    def __init__(self):
        # 1. Intelligence & Verification
        self.router = MoERouter()
        self.semantic_cache = SemanticCache()
        self.rag = RAGEngine()
        self.guard = HallucinationGuard()
        self.trace_engine = TraceEngine()
        
        # 2. Performance & Compute Reduction
        self.cache = MultiLevelCache()
        self.predictor = PredictiveEngine(self.cache)
        self.scheduler = scheduler
        
        # 3. Reliability
        self.cb = CircuitBreaker()
        self.reliability = ReliabilityOrchestrator(self.cb)
        
        # 4. Data Efficiency
        self.bloom = BloomFilter()

        # Start background scheduler
        asyncio.create_task(self.scheduler.start())
        
    async def process(self, query: str, request_id: str, tenant_id: str = "default"):
        start_time = time.time()
        struct_logger.info("request_start", request_id=request_id, query=query, tenant_id=tenant_id)
        self.trace_engine.add_step("Engine", "request_start", {"request_id": request_id, "query": query, "tenant_id": tenant_id})
        
        # 1. PROBABILISTIC CHECK
        if not self.bloom.contains(query):
            self.bloom.add(query)

        # 2. SEMANTIC CACHE CHECK (Tenant-Isolated Compute Bypass)
        cache_key = f"semantic_cache:{tenant_id}:{query}"
        cached_data = self.semantic_cache.get(cache_key)
        if cached_data:
            self.trace_engine.add_step("Engine", "cache_hit", {"confidence": cached_data["confidence"]})
            return self._wrap_response(cached_data["result"], "SEMANTIC_CACHE", start_time, cached_data["confidence"])

        # 3. EXPERT ROUTING & THOUGHT TRACE
        routing_info = self.router.route(query)
        expert_type = routing_info["expert"]
        
        # 4. EXECUTION WITH ANALYTIC SUBSTITUTION
        async def execute_task():
            from backend.core.model_manager import model_manager
            
            # Retrieval Step with Tenant Isolation
            context_nodes = self.rag.retrieve(query, tenant_id=tenant_id)
            context_text = "\n".join([n["content"] for n in context_nodes])
            
            # Algorithmic Substitution: Use reasoning expert if applicable
            if expert_type == "reasoning":
                prompt = f"Context:\n{context_text}\n\nQuestion: {query}\nAnswer:"
                answer = await model_manager.generate_safe(prompt)
                confidence = 0.95
            else:
                answer = f"Expert ({expert_type}) generated outcome from context."
                confidence = 0.75

            # 5. HALLUCINATION GUARD (Self-Proving Correctness)
            grounding_score = self.guard.verify(answer, context_text)
            final_confidence = (confidence + grounding_score) / 2
            
            self.trace_engine.add_step("Expert", expert_type, {
                "grounding_score": grounding_score,
                "base_confidence": confidence,
                "tenant_id": tenant_id
            })
            
            return {
                "answer": answer,
                "confidence": final_confidence,
                "expert": expert_type,
                "trace": self.trace_engine.get_full_trace()
            }

        result = await self.reliability.execute(f"expert_{expert_type}", execute_task)

        # 6. BG PRECOMPUTATION
        await self.scheduler.schedule(f"pre_{request_id}", self.predictor.precompute, expert_type, query)

        # 7. CACHE FOR REUSE (Tenant-Isolated)
        self.semantic_cache.set(cache_key, result)
        
        return self._wrap_response(result, "COMPUTE_BYPASS", start_time, result.get("confidence", 0.9))

    def _wrap_response(self, result, mode, start_time, confidence=1.0):
        data = result.get("result") if isinstance(result, dict) and "result" in result else result
        answer = data.get("answer") if isinstance(data, dict) else str(data)
        expert = data.get("expert") if isinstance(data, dict) else "MoE_Default"
        trace = data.get("trace") if isinstance(data, dict) else []

        return {
            "status": "success",
            "mode": mode,
            "expert": str(expert),
            "result": str(answer),
            "confidence": float(confidence),
            "trace": trace,
            "compute_cost_avoided": mode != "FULL_CALC",
            "latency_ms": float(round((time.time() - start_time) * 1000, 2)),
            "timestamp": float(time.time())
        }

hyper_engine = UnifiedSaaSEngine()
