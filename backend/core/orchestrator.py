from typing import Optional, Dict, List, Any
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
from backend.predictive.answer_store import global_predictive_store
from backend.predictive.predictor import global_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.shadow.shadow_worker import global_shadow_worker
from backend.shadow.conversation_tracker import global_tracker
from backend.core.metrics import (
    PPE_HITS, SHADOW_HITS, MODEL_INVOCATIONS, RAG_HITS, MICRO_MODEL_HITS, CACHE_HITS,
    GRAPH_HITS, TEMPLATE_HITS, ENHANCEMENT_USAGE, MODEL_CALLS_TOTAL,
    REASONING_REUSES, EARLY_EXIT_TOTAL, TOKEN_SAVINGS,
    CANONICAL_HITS, PRECOMPUTE_HITS, FAILURE_RATE, DOMAIN_REJECTIONS,
    COST_FORCED_SAVES, LATENCY_SKIPS
)
from backend.analytics.query_logger import global_query_logger

from backend.inference.kv_cache import global_kv_cache
from backend.inference.speculative_decoder import global_speculative_decoder
from backend.rag.context_compression import global_compressor
from backend.reasoning.query_planner import global_query_planner
from backend.micro_models.router import global_micro_router
from backend.learning.answer_store import global_learning_engine
from backend.inference.distributed_router import global_inference_controller

# Next-Gen 10-Layer Pipeline Imports
from backend.normalization.normalizer import global_normalizer
from backend.graph.answer_graph_engine import global_age
from backend.templates.template_engine import global_template_engine
from backend.router.query_complexity import global_complexity_estimator
from backend.memory.reasoning_store import global_reasoning_store
from backend.optimization.token_optimizer import global_token_optimizer
from backend.inference.early_exit import global_early_exit
from backend.planner.execution_planner import global_execution_planner
from backend.enhancement.enhancer import global_enhancer

# Compute-Controlled System Imports (12-Module Architecture)
from backend.domain.domain_guard import global_domain_guard
from backend.normalization.query_shaper import global_query_shaper
from backend.answers.canonical_store import global_canonical_store
from backend.answers.diff_engine import global_diff_engine
from backend.memory.global_memory import global_memory
from backend.memory.failure_store import global_failure_store
from backend.core.confidence import global_confidence_gate
from backend.core.cost_controller import global_cost_controller
from backend.core.latency_controller import global_latency_controller
from backend.predictive.precompute_expander import global_precompute_expander
from backend.predictive.user_profiler import global_user_profiler

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

        # 6. BG Workers (Will be started via start())
        self.precompute_worker_started = False

    async def start(self):
        """Initializes background workers and queues."""
        if not self.precompute_worker_started:
            from backend.predictive.precompute_worker import global_precompute_worker
            asyncio.create_task(global_precompute_worker.run())
            self.precompute_worker_started = True
            logger.info("orchestrator_background_workers_started")
        
    async def _check_persistent_cluster(self, query: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Layer 2: SQL-backed Canonical Answer Reuse."""
        from backend.core.database import SessionLocal, QueryCluster
        from sqlalchemy import text
        db = SessionLocal()
        try:
            # Simple hash check for direct hits; in a real scale, we'd use pgvector
            import hashlib
            h = hashlib.sha256(query.lower().strip().encode()).hexdigest()
            cluster = db.query(QueryCluster).filter(QueryCluster.cluster_hash == h, QueryCluster.tenant_id == tenant_id).first()
            if cluster:
                cluster.use_count += 1
                db.commit()
                return {"answer": cluster.canonical_answer, "confidence": 0.95, "canonical": True}
        except Exception as e:
            logger.error(f"persistent_cluster_error: {e}")
        finally:
            db.close()
        return None

    def _save_canonical_cluster(self, query: str, answer: str, tenant_id: str):
        """Saves a high-confidence result as a canonical cluster."""
        from backend.core.database import SessionLocal, QueryCluster
        import hashlib
        db = SessionLocal()
        try:
            h = hashlib.sha256(query.lower().strip().encode()).hexdigest()
            exists = db.query(QueryCluster).filter(QueryCluster.cluster_hash == h).first()
            if not exists:
                new_c = QueryCluster(
                    cluster_hash=h,
                    canonical_query=query,
                    canonical_answer=answer,
                    tenant_id=tenant_id
                )
                db.add(new_c)
                db.commit()
        except Exception as e:
             logger.error(f"save_cluster_error: {e}")
        finally:
            db.close()
    async def process(self, query: str, request_id: str, tenant_id: str = "default", workspace_id: str = "default"):
        """Standard entry point with multi-tenant workspace isolation."""
        start_time = time.time()
        
        # 0. ADAPTIVE LOAD SHEDDING (Disabled for Benchmarking)
        # cpu_usage = psutil.cpu_percent()
        # if cpu_usage > 99:
        #     logger.warning(f"load_shedding_active: cpu={cpu_usage}%")
        #     from fastapi import HTTPException
        #     raise HTTPException(status_code=503, detail="System under heavy load. Please try again later.")

        # 1. REQUEST DEDUPLICATION (Avoid redundant simultaneous calls)
        dedup_key = f"{tenant_id}:{workspace_id}:{query}"
        if dedup_key in self.processing:
            logger.info(f"request_deduplicated: key={dedup_key}")
            return await self.processing[dedup_key]

        task = asyncio.create_task(self._process_core(query, request_id, tenant_id, workspace_id, start_time))
        self.processing[dedup_key] = task
        try:
            result = await task
            
            # LOG FOR ANALYTICS (Phase 5)
            latency_ms = int((time.time() - start_time) * 1000)
            global_query_logger.log(
                workspace_id=workspace_id,
                user_id=request_id.split("_")[1] if "_" in request_id else "default",
                query=query,
                answer=result["result"] if isinstance(result, dict) else str(result),
                response_type=result.get("mode", "UNKNOWN"),
                latency_ms=latency_ms,
                inference_used=result.get("mode") == "FULL_CALC"
            )
            return result
        finally:
            self.processing.pop(dedup_key, None)

    async def _process_core(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float):
        logger.info(f"request_start: id={request_id} query={query} tenant={tenant_id}")
        self.trace_engine.add_step("Engine", "request_start", {"request_id": request_id, "query": query, "tenant_id": tenant_id})

        # User ID extraction for session memory
        user_id = request_id.split("_")[1] if "_" in request_id else "default"
        session_id = user_id

        # ============================================================
        # COMPUTE-CTRL GATE 0: DOMAIN CONSTRAINT CHECK
        # ============================================================
        domain_result = global_domain_guard.enforce(query)
        if not domain_result["allowed"]:
            DOMAIN_REJECTIONS.inc()
            redirect = domain_result.get("redirect", "Query outside supported domain.")
            return self._wrap_response(redirect, "DOMAIN_REJECTED", start_time, 1.0)
        # Use simplified query if domain guard simplified it
        query = domain_result.get("simplified_query") or query

        # ============================================================
        # COMPUTE-CTRL GATE 1: QUERY SHAPING (collapse variations)
        # ============================================================
        shaped = global_query_shaper.shape(query)
        shape_key = shaped["shape_key"]
        global_user_profiler.record(user_id, query, shaped)

        # ============================================================
        # COMPUTE-CTRL GATE 2: COST + LATENCY CONTROL
        # ============================================================
        global_latency_controller.start_timer(request_id)
        if global_cost_controller.should_force_cheap_path(shaped["complexity"]):
            COST_FORCED_SAVES.inc()
            logger.info(f"cost_forced_cheap: shape={shape_key}")

        # ============================================================
        # COMPUTE-CTRL GATE 3: CANONICAL STORE (HIGHEST PRIORITY)
        # ============================================================
        canonical_answer = global_canonical_store.lookup(shape_key)
        if canonical_answer:
            CANONICAL_HITS.inc()
            global_cost_controller.record("canonical", request_id)
            global_memory.log(query, canonical_answer, "CANONICAL", shape_key, 1.0,
                              global_latency_controller.elapsed_ms(request_id))
            return self._wrap_response(canonical_answer, "CANONICAL", start_time, 1.0)

        # ============================================================
        # COMPUTE-CTRL GATE 4: GLOBAL MEMORY LOOKUP (exact query reuse)
        # ============================================================
        mem_hit = global_memory.lookup(query)
        if mem_hit:
            global_cost_controller.record("canonical", request_id)
            return self._wrap_response(mem_hit["answer"], "GLOBAL_MEMORY", start_time, mem_hit["confidence"])

        # ============================================================
        # NEXT-GEN LAYER 0: QUERY NORMALIZATION + EXECUTION PLANNING
        # ============================================================
        normalized = global_normalizer.normalize(query)
        complexity = global_complexity_estimator.estimate(query, normalized)
        execution_plan = global_execution_planner.plan({**normalized, "complexity": complexity})
        # Apply latency/cost filtering to plan
        execution_plan = global_latency_controller.filter_plan(execution_plan, complexity)
        if global_cost_controller.should_force_cheap_path(complexity):
            execution_plan = global_cost_controller.force_skip_layers(execution_plan)
        self.trace_engine.add_step("Normalizer", "query_normalized", {
            "intent": normalized["intent"],
            "entity": normalized["entity"],
            "complexity": complexity,
            "plan": execution_plan[:4],
        })

        # ============================================================
        # NEXT-GEN LAYER 1: ANSWER GRAPH ENGINE (Reasoning Reuse)
        # ============================================================
        if "answer_graph" in execution_plan:
            age_result = global_age.lookup(normalized, tenant_id)
            if age_result:
                GRAPH_HITS.inc()
                EARLY_EXIT_TOTAL.inc()
                self.trace_engine.add_step("AGE", "graph_hit", {"entity": normalized["entity"]})
                return self._wrap_response(age_result, "ANSWER_GRAPH", start_time, age_result["confidence"])

        # ============================================================
        # NEXT-GEN LAYER 1b: REASONING MEMORY (Step Reuse)
        # ============================================================
        reasoning_memory = global_reasoning_store.lookup(query)
        if reasoning_memory:
            REASONING_REUSES.inc()
            EARLY_EXIT_TOTAL.inc()
            return self._wrap_response(reasoning_memory["answer"], "REASONING_MEMORY", start_time, reasoning_memory["confidence"])

        # ============================================================
        # NEXT-GEN LAYER 1c: TEMPLATE COMPILER (Zero-Cost Answers)
        # ============================================================
        if "template" in execution_plan:
            template_answer = global_template_engine.render(normalized)
            if template_answer:
                TEMPLATE_HITS.inc()
                EARLY_EXIT_TOTAL.inc()
                self.trace_engine.add_step("Template", "template_hit", {"intent": normalized["intent"]})
                # Register in graph for future reuse
                global_age.register_answer(normalized, template_answer, confidence=0.95, tenant_id=tenant_id)
                return self._wrap_response(template_answer, "TEMPLATE", start_time, 0.95)

        # 1. SHADOW ANSWER STORE (Layer 0: Predicted Match)
        shadow_hit = global_shadow_store.lookup(query, session_id, tenant_id=tenant_id, workspace_id=workspace_id)
        if shadow_hit:
            SHADOW_HITS.inc()
            self.trace_engine.add_step("Engine", "layer_0_shadow_hit", {"confidence": shadow_hit["confidence"]})
            return self._wrap_response(shadow_hit["answer"], "SHADOW_STORE", start_time, shadow_hit["confidence"])

        # 2. PREDICTIVE ANSWER STORE (Layer 1: PPE Bypass)
        predictive_hit = global_predictive_store.lookup(query, tenant_id=tenant_id, workspace_id=workspace_id)
        if predictive_hit:
            PPE_HITS.inc()
            self.trace_engine.add_step("Engine", "layer_1_predictive_hit", {"confidence": predictive_hit["confidence"]})
            return self._wrap_response(predictive_hit["answer"], "PREDICTIVE_STORE", start_time, predictive_hit["confidence"])
        
        # 3. PROMPT HASH CACHE (Layer 2: Exact match bypass)
        cached_response = check_cache(query, tenant_id=tenant_id)
        if cached_response:
             import json
             try:
                 result = json.loads(cached_response)
                 self.trace_engine.add_step("Engine", "layer_2_prompt_cache_hit", {})
                 CACHE_HITS.inc()
                 return self._wrap_response(result, "PROMPT_CACHE", start_time, 1.0)
             except:
                 pass
        
        # 4. KV-CACHE REUSE (Layer 2.5: Distributed Prompt Processing)
        kv_state = global_kv_cache.lookup_kv_state(query)
        if kv_state:
             self.trace_engine.add_step("Engine", "layer_2_5_kv_cache_hit", {})
             # In a real model, this would pass the KV state to the inference layer

        # 4. LOG QUERY FOR PPE PATTERN MINING
        global_predictor.log_query(query)

        # 3. PROBABILISTIC CHECK
        if not self.bloom.contains(query):
            self.bloom.add(query)

        # 5. SEMANTIC CACHE CHECK (Layer 3: Fast Redis Bypass)
        cache_key = f"semantic_cache:{tenant_id}:{query}"
        cached_data = self.semantic_cache.get(cache_key)
        if cached_data:
            self.trace_engine.add_step("Engine", "layer_3_semantic_cache_hit", {"confidence": cached_data["confidence"]})
            CACHE_HITS.inc()
            return self._wrap_response(cached_data["result"], "SEMANTIC_CACHE", start_time, cached_data["confidence"])

        # 6. PERSISTENT CLUSTER CHECK (Layer 4: Canonical Bypass)
        cluster_data = await self._check_persistent_cluster(query, tenant_id)
        if cluster_data:
            self.trace_engine.add_step("Engine", "layer_4_cluster_hit", {"confidence": 0.95})
            return self._wrap_response(cluster_data["answer"], "CANONICAL_CLUSTER", start_time, 0.95)

        # 5. EXPERT ROUTING & THOUGHT TRACE
        route_start = time.time()
        routing_info = self.router.route(query)
        expert_type = routing_info.get("expert", "reasoning")
        route_time = time.time() - route_start
        
        # 6. EXECUTION WITH ANALYTIC SUBSTITUTION & REASONING V3
        async def execute_task():
            # A. ADAPTIVE QUERY PLANNING
            planned_ans = await global_query_planner.execute_plan(query)
            if planned_ans:
                return {"answer": planned_ans, "expert": "planner", "confidence": 0.95}

            # B. Retrieval Step with Tenant Isolation & Timing
            retrieval_start = time.time()
            context_nodes = self.rag.retrieve(query, tenant_id=tenant_id)
            RAG_HITS.inc()
            retrieval_time = time.time() - retrieval_start
            
            # C. CONTEXT COMPRESSION
            raw_context = [n["content"] for n in context_nodes]
            compressed_context = global_compressor.compress(raw_context)
            self.trace_engine.add_step("RAG", "context_compressed", {"original_len": len(" ".join(raw_context))})

            # DLSS INTERCEPTION: Attempt to enhance raw RAG context into a final answer
            from backend.enhancement.enhancement_pipeline import global_enhancement_pipeline
            from backend.core.metrics import ENHANCEMENT_ATTEMPTS, ENHANCEMENT_SUCCESS, MODEL_BYPASS_VIA_ENHANCEMENT

            ENHANCEMENT_ATTEMPTS.inc()
            # We treat the fast compressed context as the "raw answer"
            intent = normalized.get("intent", "general") if 'normalized' in locals() else "general"
            enhanced, status = global_enhancement_pipeline.run(compressed_context, query, raw_context, intent)
            
            if status == "enhancement_success":
                ENHANCEMENT_SUCCESS.inc()
                MODEL_BYPASS_VIA_ENHANCEMENT.inc()
                self.trace_engine.add_step("DLSS_Enhancer", "model_bypassed", {"status": "success"})
                return {
                    "answer": enhanced, 
                    "expert": "DLSS_Answer_Reconstruction", 
                    "confidence": 0.88,
                    "metrics": {"total_ms": round((time.time() - start_time) * 1000, 2)}
                }

            # D. MICRO-MODEL SPECIALIZATION
            specialty = global_micro_router.route(query)
            if specialty:
                MICRO_MODEL_HITS.inc()
                ans = await global_micro_router.execute(query, specialty)
                return {"answer": ans, "expert": specialty, "confidence": 0.98}
            
            # E. SPECULATIVE DECODING with DIGITAL TWIN
            reasoning_start = time.time()
            from backend.intelligence.reasoning import reasoning_expert
            
            # Use Speculative Decoder for generation prediction
            speculative_ans = await global_speculative_decoder.generate(query)
            
            result_data = await reasoning_expert.solve(
                query, 
                context=[compressed_context], 
                session_id=session_id, 
                tenant_id=tenant_id
            )
            
            # In a real system, we'd accept the speculative_ans if the verifier (reasoning_expert) agrees
            # Here we simulate the blend
            result_data["answer"] = speculative_ans if result_data.get("confidence", 0) > 0.9 else result_data["answer"]
            
            reasoning_time = time.time() - reasoning_start

            # Hallucination Guard (Final Check)
            guard_start = time.time()
            grounding_score = self.guard.verify(result_data["answer"], raw_context)
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
        
        async def execute_task_with_logging():
            try:
                return await execute_task()
            except Exception as e:
                logger.exception(f"execute_task_failed: {e}")
                raise e

        MODEL_INVOCATIONS.inc()
        # F. DISTRIBUTED INFERENCE ROUTING
        result = await global_inference_controller.route_job(
            self.reliability.execute, f"expert_{expert_type}", execute_task_with_logging
        )

        # Ensure result is a dictionary (handle reliability fallback string)
        if isinstance(result, str):
            logger.warning(f"fallback_triggered: {result}")
            result = {
                "answer": result,
                "confidence": 0.0,
                "mode": "FALLBACK",
                "expert": "reliability_layer"
            }

        # G. CONTINUOUS LEARNING
        if result.get("confidence", 0) > 0.9:
            await global_learning_engine.learn(
                query, 
                result["answer"], 
                result.get("confidence", 0), 
                tenant_id=tenant_id, 
                workspace_id=workspace_id
            )
            # NEXT-GEN: Register high-confidence results into Answer Graph for future reuse
            global_age.register_answer(
                normalized_query=normalized,
                answer=result["answer"],
                confidence=result.get("confidence", 0.9),
                steps=result.get("trace", {}).get("steps", []),
                tenant_id=tenant_id,
            )
            # NEXT-GEN: Store reasoning steps for future path reuse
            global_reasoning_store.store(
                query=query,
                steps=result.get("trace", {}).get("steps", []),
                answer=result["answer"],
                confidence=result.get("confidence", 0.9),
            )

        # NEXT-GEN: POST-INFERENCE ANSWER ENHANCEMENT (DLSS Layer)
        raw_answer = result.get("answer", "")
        if raw_answer:
            context_docs = [n.get("content", "") for n in self.rag.retrieve(query, tenant_id=tenant_id)] if result.get("mode") == "FULL_CALC" else []
            enhanced = global_enhancer.enhance(raw_answer, query, context_docs)
            if enhanced.get("enhanced"):
                ENHANCEMENT_USAGE.inc()
                result["answer"] = enhanced["answer"]
                result["quality_score"] = enhanced.get("quality_score", 0.9)

        # NEXT-GEN: Token savings telemetry
        MODEL_CALLS_TOTAL.inc()
        opt_result = global_token_optimizer.optimize(query)
        TOKEN_SAVINGS.set(opt_result["token_reduction"])

        # 6. BG PRECOMPUTATION
        # Use scheduler for non-critical path
        asyncio.create_task(self.scheduler.schedule(f"pre_{request_id}", global_predictor.mine_patterns))

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
            # Save to Knowledge Graph / RAG
            await self.scheduler.schedule(
                f"learn_{request_id}", 
                self.rag.add_documents, 
                [f"Q: {query}\nA: {result['answer']}"], 
                tenant_id
            )
            # Save as Canonical Cluster (Layer 2 Persistence)
            self._save_canonical_cluster(query, result["answer"], tenant_id)

        # 10. AUDIT LOG (Phase 12 Compliance)
        from backend.core.audit import audit
        audit.log_event(
            action="ai_orchestration",
            user_id=user_id,
            tenant_id=tenant_id,
            metadata={"expert": str(result.get("expert")), "mode": "FULL_CALC", "confidence": result.get("confidence")}
        )

        # 11. SHADOW PREDICTION (Accelerate future turns)
        asyncio.create_task(global_shadow_worker.precompute_next_turns(query, session_id, tenant_id))
        global_tracker.track(session_id, query)

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
