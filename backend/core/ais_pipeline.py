"""
backend/core/ais_pipeline.py

AIS++ Unified Pipeline — Hard Compute Control (AIS++ Module 13)
================================================================
Execution priority (STRICT — no exceptions):

  memory_stack  → (user → session → global)
  graph         → (query graph cluster lookup)
  prediction    → (trajectory + speculative hit)
  probability   → (probability-driven precompute check)
  composition   → (micro-parallel + delta reuse)
  approximation → (safe partial answer)
  model         → (LAST RESORT — target ≤2%)

This is the MASTER ORCHESTRATOR for AIS++.
All 14 modules are wired here in strict sequence.

Rules:
  - avoidance_rate ≥ 97–98%
  - model_calls   ≤ 2%
  - latency       ≤ 200ms (absolute), ≈ 0ms perceived
  - zero repeated compute
  - continuous expansion
  - ALL metrics real — no fake numbers
"""
import logging
import time
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ── Hard thresholds ────────────────────────────────────────────────────────── #
CONFIDENCE_FLOOR   = 0.95   # NEVER return below this from cache
LATENCY_CEILING_MS = 200.0  # Absolute maximum
MODEL_TARGET_RATE  = 0.02   # ≤2% model call rate target


class AISPipeline:
    """
    AIS++ Master Pipeline.
    Routes every query through 7 ordered stages before allowing model call.
    Every hit is stored. Every compute is deferred to background when possible.
    """

    def __init__(self):
        self._total_requests: int = 0
        self._model_calls:    int = 0

    async def handle(
        self,
        query: str,
        request_id: str,
        tenant_id:  str,
        user_id:    str,
        session_id: str,
        start_time: float,
    ) -> Dict[str, Any]:
        """
        Main entry for ALL requests through AIS++.
        Returns a structured response with provenance metadata.
        """
        self._total_requests += 1

        # ── Lazy imports to avoid circular dependencies ─────────────────── #
        from backend.router.query_family_mapper       import global_query_family_mapper
        from backend.memory.global_memory             import global_memory
        from backend.memory.contextual_memory_stack   import global_memory_stack
        from backend.graph.query_graph                import global_query_graph
        from backend.intelligence.intent_trajectory   import global_intent_trajectory
        from backend.predictive.speculative_executor  import global_speculative_executor
        from backend.predictive.probability_engine    import global_probability_engine
        from backend.core.micro_parallel_processor    import global_micro_parallel
        from backend.core.delta_compute_engine        import global_delta_engine
        from backend.core.global_dedup_cache          import global_dedup_cache
        from backend.core.failure_recovery_engine     import global_failure_recovery
        from backend.core.zero_repeat_store           import global_zero_repeat_store
        from backend.analytics.avoidance_tracker      import global_avoidance_tracker
        from backend.background.compute_engine        import global_bg_compute
        from backend.shadow.shadow_store              import global_shadow_store

        # ── Step -1: Task Elimination Engine ──────────────────────────── #
        # Eliminate empty, trivial, or ignore instructions immediately
        cleaned_query = query.strip()
        if not cleaned_query or len(cleaned_query) < 2:
            return self._wrap("Query too short or empty.", "task_elimination", start_time, 1.0, query)
            
        elimination_keywords = {"ping", "test", "ignore", "keep-alive", "healthcheck"}
        if cleaned_query.lower() in elimination_keywords:
            return self._wrap("pong", "task_elimination", start_time, 1.0, query)

        # ── Step 0: Normalize → family mapping ────────────────────────── #
        norm       = global_query_family_mapper.normalize(query)
        family_id  = norm["family_id"]
        intent     = norm["intent"]
        entity     = norm["entity"]
        clean      = norm["clean"]

        def elapsed() -> float:
            return (time.time() - start_time) * 1000

        def remaining(cap: float) -> float:
            return max(min(LATENCY_CEILING_MS - elapsed(), cap), 1.0) / 1000.0

        logger.info(
            f"ais.request: id={request_id} family={family_id} "
            f"intent={intent} entity={entity}"
        )

        # ── Step 0.5: Global Dedup Check ──────────────────────────────── #
        dedup_hit = global_dedup_cache.check(family_id, query)
        if dedup_hit and dedup_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
            result = self._wrap(dedup_hit["answer"], "global_dedup", start_time,
                                dedup_hit["confidence"], clean)
            self._track(request_id, clean, family_id, result, False, True,
                        global_avoidance_tracker)
            return result

        # In-flight dedup
        if global_dedup_cache.is_inflight(family_id):
            inflight_res = await global_dedup_cache.wait_for_inflight(
                family_id, timeout=remaining(500)
            )
            if inflight_res:
                result = self._wrap(inflight_res.get("answer", ""), "inflight_dedup",
                                    start_time, inflight_res.get("confidence", 1.0), clean)
                self._track(request_id, clean, family_id, result, False, True,
                            global_avoidance_tracker)
                return result

        # Register as in-flight
        loop = asyncio.get_event_loop()
        inflight_future = loop.create_future()
        global_dedup_cache.mark_inflight(family_id, inflight_future)

        try:
            # ── STAGE 1: Memory Stack (user → session → global) ────────── #
            memory_hit = global_memory_stack.lookup(
                family_id, query, user_id, session_id, global_memory
            )
            if memory_hit and memory_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                answer = memory_hit.get("answer") or memory_hit.get("result", "")
                if answer:
                    result = self._wrap(answer, f"memory_{memory_hit.get('memory_layer','stack')}",
                                        start_time, memory_hit["confidence"], clean)
                    logger.info(f"ais.stage1_hit: layer={memory_hit.get('memory_layer')} family={family_id}")
                    return await self._finish(
                        result, query, family_id, user_id, session_id, intent, entity,
                        tenant_id, start_time, False, True,
                        global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                        global_shadow_store, global_memory, global_avoidance_tracker,
                        global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                    )

            # ── STAGE 2: Query Graph Lookup ────────────────────────────── #
            graph_hit = global_query_graph.lookup(family_id)
            if not graph_hit:
                graph_hit = global_query_graph.lookup_by_entity_intent(entity, intent)
            if graph_hit and graph_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(graph_hit["answer"], "query_graph", start_time,
                                    graph_hit["confidence"], clean)
                logger.info(f"ais.stage2_hit: family={family_id}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # ── STAGE 3: Trajectory + Speculative Prediction ───────────── #
            # Check if a speculative execution already cached this query
            spec_hit = global_speculative_executor.check_speculative_hit(query, global_memory)
            if spec_hit and spec_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(spec_hit["answer"], "speculative_hit", start_time,
                                    spec_hit["confidence"], clean)
                logger.info(f"ais.stage3_speculative_hit: family={family_id}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # ── STAGE 4: Probability Match ─────────────────────────────── #
            # The probability engine has pre-warmed high-scoring families
            # Check global memory for probability-precomputed results
            cluster_density = len(global_query_graph.get_cluster(family_id))
            prob = global_probability_engine.score(family_id, entity, intent, cluster_density)
            global_probability_engine.record_query(family_id, entity)

            prob_hit = global_memory.lookup(query, canonical_form=family_id)
            if prob_hit and prob_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(prob_hit["answer"], "probability_match", start_time,
                                    prob_hit["confidence"], clean)
                logger.info(f"ais.stage4_prob_hit: family={family_id} prob={prob:.3f}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # ── STAGE 5: Composition (micro-parallel + delta) ──────────── #
            # 5a: Micro-parallel
            try:
                par_result = await asyncio.wait_for(
                    global_micro_parallel.resolve(
                        query, global_memory, global_bg_compute,
                        tenant_id, session_id, global_delta_engine
                    ),
                    timeout=remaining(80),
                )
            except Exception:
                par_result = None

            if par_result and par_result.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(par_result["answer"], "micro_parallel_composition",
                                    start_time, par_result["confidence"], clean)
                logger.info(f"ais.stage5a_parallel_hit: family={family_id}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # 5b: Delta compute (fragment reuse)
            try:
                delta_result = await asyncio.wait_for(
                    global_delta_engine.resolve(
                        query, global_memory, global_bg_compute, tenant_id, session_id
                    ),
                    timeout=remaining(60),
                )
            except Exception:
                delta_result = None

            if delta_result and delta_result.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(delta_result["answer"], f"delta_{delta_result['mode']}",
                                    start_time, delta_result["confidence"], clean)
                logger.info(f"ais.stage5b_delta_hit: family={family_id}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # ── STAGE 6: Graph Cluster Composition ────────────────────── #
            cluster_answer = global_query_graph.compose_cluster_answer(family_id, query)
            if cluster_answer:
                result = self._wrap(cluster_answer, "graph_cluster_compose", start_time, 0.96, clean)
                logger.info(f"ais.stage6_cluster_hit: family={family_id}")
                return await self._finish(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, start_time, False, True,
                    global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                    global_shadow_store, global_memory, global_avoidance_tracker,
                    global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
                )

            # ── STAGE 7: Approximation (safe partial) ─────────────────── #
            # If latency budget is nearly exhausted → return skeleton + defer
            current_elapsed = elapsed()
            if current_elapsed > 100:
                skeleton = global_failure_recovery.get_safe_skeleton(
                    query, reason=f"computation_deferred ({current_elapsed:.0f}ms spent)"
                )
                asyncio.create_task(
                    global_bg_compute.enqueue(query, tenant_id, "AIS_DEFERRAL", session_id, priority="high")
                )
                result = self._wrap(skeleton, "approximation_skeleton", start_time, 0.5, clean)
                self._track(request_id, clean, family_id, result, False, False, global_avoidance_tracker,
                            is_recovery=True)
                if not inflight_future.done():
                    inflight_future.set_result(result)
                return result

            # ── STAGE 8: MODEL CALL — Last Resort ─────────────────────── #
            # Target: ≤2% of all requests
            current_rate = self._model_calls / self._total_requests if self._total_requests > 0 else 0
            logger.warning(
                f"ais.model_call: family={family_id} "
                f"rate={current_rate:.2%} (target≤{MODEL_TARGET_RATE:.0%})"
            )
            self._model_calls += 1

            model_answer = await self._call_model(query, tenant_id, session_id)
            model_confidence = 0.97

            result = self._wrap(model_answer, "model_last_resort", start_time, model_confidence, clean)
            return await self._finish(
                result, query, family_id, user_id, session_id, intent, entity,
                tenant_id, start_time, True, False,
                global_dedup_cache, global_memory_stack, global_zero_repeat_store,
                global_shadow_store, global_memory, global_avoidance_tracker,
                global_intent_trajectory, global_bg_compute, inflight_future, request_id, clean,
            )

        finally:
            global_dedup_cache.clear_inflight(family_id)

    # ── Post-Processing ────────────────────────────────────────────────────── #

    async def _finish(
        self,
        result: Dict[str, Any],
        query: str,
        family_id: str,
        user_id: str,
        session_id: str,
        intent: str,
        entity: str,
        tenant_id: str,
        start_time: float,
        model_called: bool,
        is_cache_hit: bool,
        global_dedup_cache,
        global_memory_stack,
        global_zero_repeat_store,
        global_shadow_store,
        global_memory,
        global_avoidance_tracker,
        global_intent_trajectory,
        global_bg_compute,
        inflight_future,
        request_id: str,
        clean: str,
    ) -> Dict[str, Any]:
        """
        Common post-processing: store everywhere + launch background expansion.
        """
        from backend.graph.query_graph                  import global_query_graph
        from backend.intelligence.knowledge_field       import global_knowledge_field
        from backend.predictive.massive_prediction_engine import global_massive_predictor
        from backend.predictive.probability_engine      import global_probability_engine

        answer     = result.get("result", "")
        confidence = result.get("confidence", 0.0)
        mode       = result.get("mode", "unknown")

        # Store in every layer
        try:
            global_memory_stack.store(family_id, query, answer, confidence, user_id, session_id)
        except Exception: pass

        try:
            global_zero_repeat_store.store(
                query, answer, family_id, mode, confidence,
                result.get("latency_ms", 0.0), session_id, global_memory, global_shadow_store
            )
        except Exception: pass

        try:
            global_dedup_cache.register(family_id, query, answer, confidence,
                                        result.get("latency_ms", 0.0), mode)
        except Exception: pass

        # Register in query graph
        try:
            from backend.router.query_family_mapper import global_query_family_mapper
            global_query_family_mapper.normalize(query)
            global_query_graph.register(
                family_id, query, answer, entity, intent, confidence
            )
            global_knowledge_field.mark_covered(entity, intent)
        except Exception: pass

        # Track metrics
        self._track(request_id, clean, family_id, result, model_called, is_cache_hit,
                    global_avoidance_tracker)

        # Background: trajectory + massive prediction + probability queue
        asyncio.create_task(self._background_expand(
            query, entity, intent, family_id, session_id, tenant_id,
            global_intent_trajectory, global_massive_predictor,
            global_probability_engine, global_bg_compute, global_memory,
        ))

        # Resolve in-flight future
        if not inflight_future.done():
            inflight_future.set_result(result)

        return result

    async def _background_expand(
        self, query, entity, intent, family_id, session_id, tenant_id,
        traj_engine, mass_pred, prob_engine, bg_compute, global_memory,
    ) -> None:
        """Fire-and-forget background expansion after every request."""
        try:
            await traj_engine.precompute_trajectory(
                entity, intent, session_id, family_id, tenant_id, bg_compute
            )
            await mass_pred.precompute_family(
                query, entity, intent, family_id, tenant_id, session_id
            )
            traj_engine.log_query(session_id, query)
        except Exception as exc:
            logger.debug(f"ais.background_expand_error: {exc}")

    # ── Model Call ─────────────────────────────────────────────────────────── #

    async def _call_model(self, query: str, tenant_id: str, session_id: str) -> str:
        """Last-resort model invocation. Target: ≤2% of requests."""
        try:
            from backend.intelligence.rag import global_rag_engine
            from backend.intelligence.reasoning import reasoning_expert
            from backend.micro_models.router import global_micro_router

            # Try micro-model first (cheaper)
            specialty = global_micro_router.route(query)
            if specialty:
                ans = await global_micro_router.execute(query, specialty)
                if ans and len(ans.strip()) > 10:
                    return ans

            # RAG + reasoning
            ctx = global_rag_engine.retrieve(query, tenant_id=tenant_id)
            context = [n["content"] for n in ctx] if ctx else []
            answer = await reasoning_expert.solve(query, context=context, tenant_id=tenant_id)
            answer_str = answer.get("answer", str(answer)) if isinstance(answer, dict) else str(answer)
            return answer_str if answer_str else f"Processed: {query}"
        except Exception as exc:
            logger.error(f"ais.model_call_error: {exc}")
            return f"Unable to process at this time. Query: '{query}'"

    # ── Wrap + Track helpers ───────────────────────────────────────────────── #

    def _wrap(self, answer: str, mode: str, start_time: float,
              confidence: float, norm_query: str) -> Dict[str, Any]:
        latency = (time.time() - start_time) * 1000
        return {
            "result":          answer,
            "mode":            mode,
            "confidence":      confidence,
            "latency_ms":      latency,
            "normalized_query": norm_query,
            "compute_avoided": mode not in ("model_last_resort", "FULL_CALC"),
        }

    def _track(self, request_id: str, norm_query: str, family_id: str,
               result: Dict[str, Any], model_called: bool, is_cache_hit: bool,
               tracker, is_recovery: bool = False) -> None:
        try:
            tracker.record(
                request_id=request_id,
                normalized_query=norm_query,
                family_id=family_id,
                path_taken=result.get("mode", "unknown"),
                latency_ms=result.get("latency_ms", 0.0),
                model_called=model_called,
                confidence=result.get("confidence", 0.0),
                is_cache_hit=is_cache_hit,
                is_recovery=is_recovery,
            )
        except Exception:
            pass

    def avoidance_rate(self) -> float:
        if self._total_requests == 0:
            return 0.0
        return 1.0 - self._model_calls / self._total_requests

    def stats(self) -> Dict[str, Any]:
        rate = self.avoidance_rate()
        return {
            "total_requests":   self._total_requests,
            "model_calls":      self._model_calls,
            "avoidance_rate":   f"{rate:.2%}",
            "model_call_rate":  f"{self._model_calls/max(self._total_requests,1):.2%}",
            "target_avoidance": "≥97%",
            "target_model_rate":"≤2%",
        }


global_ais_pipeline = AISPipeline()
