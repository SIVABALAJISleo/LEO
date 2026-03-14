from backend.intelligence.router import MoERouter, SemanticCache, HallucinationGuard, TraceEngine
from backend.intelligence.rag import RAGEngine
from backend.intelligence.reasoning import reasoning_expert
from backend.performance.caching import MultiLevelCache, PredictiveEngine
from backend.performance.memo import global_memo
from backend.performance.scheduler import scheduler
from backend.core.reliability import CircuitBreaker, ReliabilityOrchestrator
from backend.data_efficiency.probabilistic import BloomFilter
import logging
import time
import asyncio
import psutil
from backend.core.prompt_cache import check_cache, save_cache

logger = logging.getLogger(__name__)

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
        
        # 5. In-flight Request Deduplication
        self.processing: Dict[str, asyncio.Task] = {}

        # Start background scheduler (Moved to lazy start or startup event)
        # asyncio.create_task(self.scheduler.start())
        
    async def process(self, query: str, request_id: str, tenant_id: str = "default"):
        start_time = time.time()
        
        # 0. ADAPTIVE LOAD SHEDDING
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > 90:
            logger.warning(f"load_shedding_active: cpu={cpu_usage}%")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="System under heavy load. Please try again later.")

        # 1. REQUEST DEDUPLICATION (Avoid redundant simultaneous calls)
        dedup_key = f"{tenant_id}:{query}"
        if dedup_key in self.processing:
            logger.info(f"request_deduplicated: key={dedup_key}")
            return await self.processing[dedup_key]

        task = asyncio.create_task(self._process_core(query, request_id, tenant_id, start_time))
        self.processing[dedup_key] = task
        try:
            return await task
        finally:
            self.processing.pop(dedup_key, None)

    async def _process_core(self, query: str, request_id: str, tenant_id: str, start_time: float):
        logger.info(f"request_start: id={request_id} query={query} tenant={tenant_id}")
        self.trace_engine.add_step("Engine", "request_start", {"request_id": request_id, "query": query, "tenant_id": tenant_id})
        
        # User ID extraction for session memory
        user_id = request_id.split("_")[1] if "_" in request_id else "default"
        session_id = user_id # Using user_id as session_id for continuity

        # 2. PROMPT HASH CACHE (Exact match bypass)
        cached_response = check_cache(query, tenant_id=tenant_id)
        if cached_response:
             import json
             try:
                 result = json.loads(cached_response)
                 self.trace_engine.add_step("Engine", "prompt_cache_hit", {})
                 return self._wrap_response(result, "PROMPT_CACHE", start_time, 1.0)
             except:
                 pass

        # 3. PROBABILISTIC CHECK
        if not self.bloom.contains(query):
            self.bloom.add(query)

        # 4. SEMANTIC CACHE CHECK (Tenant-Isolated Compute Bypass)
        cache_key = f"semantic_cache:{tenant_id}:{query}"
        cached_data = self.semantic_cache.get(cache_key)
        if cached_data:
            self.trace_engine.add_step("Engine", "cache_hit", {"confidence": cached_data["confidence"]})
            return self._wrap_response(cached_data["result"], "SEMANTIC_CACHE", start_time, cached_data["confidence"])

        # 5. EXPERT ROUTING & THOUGHT TRACE
        route_start = time.time()
        routing_info = self.router.route(query)
        expert_type = routing_info.get("expert", "reasoning")
        route_time = time.time() - route_start
        
        # 6. EXECUTION WITH ANALYTIC SUBSTITUTION & REASONING V3
        async def execute_task():
            # Retrieval Step with Tenant Isolation & Timing
            retrieval_start = time.time()
            context_nodes = self.rag.retrieve(query, tenant_id=tenant_id)
            retrieval_time = time.time() - retrieval_start
            context_docs = [n["content"] for n in context_nodes]
            
            # Cogntive Execution Step
            reasoning_start = time.time()
            # We use reasoning_expert for ALL reasoning/complex intents.
            # Other experts (code, etc.) would be integrated similarly.
            from backend.intelligence.reasoning import reasoning_expert
            result_data = await reasoning_expert.solve(
                query, 
                context=context_docs, 
                session_id=session_id, 
                tenant_id=tenant_id
            )
            reasoning_time = time.time() - reasoning_start

            # Hallucination Guard (Final Check)
            guard_start = time.time()
            grounding_score = self.guard.verify(result_data["answer"], context_docs)
            guard_time = time.time() - guard_start
            
            final_confidence = (result_data.get("confidence", 0.5) + grounding_score) / 2
            
            self.trace_engine.add_step("Expert", expert_type, {
                "grounding_score": grounding_score,
                "tenant_id": tenant_id,
                "steps": result_data.get("steps", []),
                "metrics": {
                    "retrieval_ms": round(retrieval_time * 1000, 2),
                    "reasoning_ms": round(reasoning_time * 1000, 2),
                    "guard_ms": round(guard_time * 1000, 2)
                }
            })
            
            return {
                "answer": result_data["answer"],
                "confidence": final_confidence,
                "expert": expert_type,
                "metrics": {
                    "route_ms": round(route_time * 1000, 2),
                    "retrieval_ms": round(retrieval_time * 1000, 2),
                    "reasoning_ms": round(reasoning_time * 1000, 2),
                    "guard_ms": round(guard_time * 1000, 2),
                    "total_ms": round((time.time() - start_time) * 1000, 2)
                },
                "trace": self.trace_engine.get_full_trace()
            }

        result = await self.reliability.execute(f"expert_{expert_type}", execute_task)

        # 6. BG PRECOMPUTATION
        await self.scheduler.schedule(f"pre_{request_id}", self.predictor.precompute, expert_type, query)

        # 7. CACHE FOR REUSE (Tenant-Isolated)
        self.semantic_cache.set(cache_key, result)
        import json
        save_cache(query, json.dumps(result), tenant_id=tenant_id)
        
        # 8. RECORD USAGE (SaaS Business Layer)
        from backend.core.database import SessionLocal
        from backend.core.metering import record_ai_usage
        db = SessionLocal()
        try:
            tokens = (len(query) + len(result.get("answer", ""))) // 4
            latency_ms = int((time.time() - start_time) * 1000)
            record_ai_usage(db, tenant_id, user_id, tokens, latency_ms)
        finally:
            db.close()

        # 9. AUTONOMOUS LEARNING (Phase 18 Feedback Loop)
        if result.get("confidence", 0) > 0.92:
            await self.scheduler.schedule(
                f"learn_{request_id}", 
                self.rag.add_documents, 
                [f"Q: {query}\nA: {result['answer']}"], 
                tenant_id
            )

        # 10. AUDIT LOG (Phase 12 Compliance)
        from backend.core.audit import audit
        audit.log_event(
            action="ai_orchestration",
            user_id=user_id,
            tenant_id=tenant_id,
            metadata={"expert": str(result.get("expert")), "mode": "FULL_CALC", "confidence": result.get("confidence")}
        )

        return self._wrap_response(result, "FULL_CALC", start_time, result.get("confidence", 0.9))

    async def process_stream(self, query: str, request_id: str, tenant_id: str = "default"):
        """Streaming version of the orchestration process."""
        start_time = time.time()
        
        # 0. ADAPTIVE LOAD SHEDDING
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > 90:
            yield f"Error: System under heavy load ({cpu_usage}%)."
            return

        user_id = request_id.split("_")[1] if "_" in request_id else "default"
        
        # 1. RETRIEVAL
        context_nodes = self.rag.retrieve(query, tenant_id=tenant_id)
        context_docs = [n["content"] for n in context_nodes]
        
        # 2. STREAMING REASONING
        from backend.intelligence.reasoning import reasoning_expert
        async for chunk in reasoning_expert.solve_stream(
            query, 
            context=context_docs, 
            session_id=user_id, 
            tenant_id=tenant_id
        ):
            yield chunk

        # 3. BG LOGGING & USAGE
        from backend.core.database import SessionLocal
        from backend.core.metering import record_usage
        db = SessionLocal()
        try:
            record_usage(db, tenant_id, user_id, "request_stream", 1)
        finally:
            db.close()

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
