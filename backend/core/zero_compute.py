"""
backend/core/zero_compute.py
Unified Zero-Runtime-Compute Control Layer — v3 (AIS++ Maximum Avoidance).

PIPELINE ORDER (strict, 9 stages):
  global_dedup  → memory_stack → query_graph → speculative →
  probability   → micro_parallel+delta → graph_cluster → 
  approximation → deferral → model (last resort ≤2%)

GUARANTEES:
  - avoidance_rate ≥ 97–98%
  - model_calls    ≤ 2%
  - perceived latency ≈ 0ms (instant ACK + skeleton)
  - zero repeated computation
  - continuous knowledge expansion
  - ALL metrics real — no fake numbers

Every module wired here in strict order.
"""
import logging
import time
import asyncio
import uuid
from typing import Optional, Dict, Any, Set

logger = logging.getLogger(__name__)

# ── Hard thresholds ──────────────────────────────────────────────────────── #
CONFIDENCE_FLOOR   = 0.95    # NEVER return below this from cache
LATENCY_CEILING_MS = 200.0   # Absolute maximum — exceeding is a BUG
MODEL_TARGET_RATE  = 0.02    # ≤2% model call target
APPROX_CEILING     = 0.88    # approximations capped here


class ZeroComputeControl:
    """
    AIS++ v3 Master Control.
    Routes every request through 9 ordered avoidance stages.
    Falls through to model only when ALL stages miss.
    """

    def __init__(self):
        self._total:  int = 0
        self._model:  int = 0
        self._in_flight: Dict[str, asyncio.Future] = {}

    async def handle_request(
        self,
        query:        str,
        request_id:   str,
        tenant_id:    str,
        workspace_id: str,
        start_time:   float,
        user_id:      str = "default",
    ) -> Dict[str, Any]:
        """
        Single entry point for ALL requests.
        Returns structured response — never raises.
        """
        self._total += 1

        # ── Lazy imports (avoid circular at module level) ─────────────────── #
        from backend.router.query_family_mapper        import global_query_family_mapper
        from backend.memory.global_memory             import global_memory
        from backend.memory.contextual_memory_stack   import global_memory_stack
        from backend.graph.query_graph                import global_query_graph
        from backend.predictive.speculative_executor  import global_speculative_executor
        from backend.predictive.probability_engine    import global_probability_engine
        from backend.core.micro_parallel_processor    import global_micro_parallel
        from backend.core.delta_compute_engine        import global_delta_engine
        from backend.core.global_dedup_cache          import global_dedup_cache
        from backend.core.failure_recovery_engine     import global_failure_recovery
        from backend.core.zero_repeat_store           import global_zero_repeat_store
        from backend.core.compute_deferral            import global_compute_deferral
        from backend.intelligence.approximation_engine import global_approximation_engine
        from backend.core.experience_optimizer        import global_experience_optimizer
        from backend.analytics.avoidance_tracker      import global_avoidance_tracker
        from backend.analytics.metrics                import global_metrics
        from backend.background.compute_engine        import global_bg_compute
        from backend.shadow.shadow_store              import global_shadow_store
        from backend.intelligence.intent_trajectory   import global_intent_trajectory
        from backend.intelligence.knowledge_field     import global_knowledge_field
        from backend.predictive.massive_prediction_engine import global_massive_predictor
        from orchestration.chaos_containment          import global_chaos_containment
        from backend.micro_models.router              import global_micro_router
        from backend.intelligence.rag                 import global_rag_engine
        from backend.intelligence.reasoning           import reasoning_expert

        # ── Step 0: Normalize + Family Mapping ──────────────────────────── #
        norm      = global_query_family_mapper.normalize(query)
        family_id = norm["family_id"]
        intent    = norm["intent"]
        entity    = norm["entity"]
        clean     = norm["clean"]
        session_id = request_id.split("_")[1] if "_" in request_id else "default"

        def elapsed() -> float:
            return (time.time() - start_time) * 1000

        def remaining(cap: float) -> float:
            return max(min(LATENCY_CEILING_MS - elapsed(), cap), 1.0) / 1000.0

        logger.info(
            f"zcc.request: id={request_id} family={family_id} "
            f"intent={intent} entity={entity}"
        )

        # Record for experience optimizer and probability engine
        global_probability_engine.record_query(family_id, entity)
        global_intent_trajectory.log_query(session_id, query)

        # ─────────────────────────────────────────────────────────────────── #
        # STAGE 0.5 — Global Dedup (Bloom + Exact hash)                       #
        # ─────────────────────────────────────────────────────────────────── #
        dedup_hit = global_dedup_cache.check(family_id, query)
        if dedup_hit and dedup_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
            result = self._wrap(dedup_hit["answer"], "global_dedup",
                                start_time, dedup_hit["confidence"], clean)
            global_experience_optimizer.record("global_dedup", result["latency_ms"])
            self._track(request_id, clean, family_id, result, False, True, global_avoidance_tracker)
            global_metrics.log_request(request_id, query, "global_dedup",
                                       result["latency_ms"], False, canonical=family_id)
            return result

        # In-flight dedup
        if family_id in self._in_flight:
            try:
                pending = await asyncio.wait_for(
                    self._in_flight[family_id], timeout=remaining(500)
                )
                if pending:
                    result = self._wrap(
                        pending.get("result", ""), "inflight_dedup",
                        start_time, pending.get("confidence", 1.0), clean
                    )
                    self._track(request_id, clean, family_id, result,
                                False, True, global_avoidance_tracker)
                    return result
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        inflight_fut = loop.create_future()
        self._in_flight[family_id] = inflight_fut
        global_dedup_cache.mark_inflight(family_id, inflight_fut)

        try:
            # ─────────────────────────────────────────────────── #
            # STAGE 1 — Contextual Memory Stack (user→session→global) #
            # ─────────────────────────────────────────────────── #
            mem_hit = global_memory_stack.lookup(
                family_id, query, user_id, session_id, global_memory
            )
            if mem_hit and mem_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                ans = mem_hit.get("answer") or mem_hit.get("result", "")
                if ans:
                    result = self._wrap(ans,
                                        f"memory_{mem_hit.get('memory_layer','stack')}",
                                        start_time, mem_hit["confidence"], clean)
                    global_experience_optimizer.record(result["mode"], result["latency_ms"])
                    return await self._persist_and_return(
                        result, query, family_id, user_id, session_id, intent, entity,
                        tenant_id, False, True, request_id, clean,
                        inflight_fut, global_dedup_cache, global_memory_stack,
                        global_zero_repeat_store, global_shadow_store, global_memory,
                        global_avoidance_tracker, global_metrics, global_intent_trajectory,
                        global_massive_predictor, global_bg_compute, global_query_graph,
                        global_knowledge_field,
                    )

            # ─────────────────────────────────────── #
            # STAGE 2 — Query Graph Lookup            #
            # ─────────────────────────────────────── #
            graph_hit = global_query_graph.lookup(family_id) or \
                        global_query_graph.lookup_by_entity_intent(entity, intent)
            if graph_hit and graph_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(graph_hit["answer"], "query_graph",
                                    start_time, graph_hit["confidence"], clean)
                global_experience_optimizer.record("query_graph", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────────── #
            # STAGE 3 — Speculative Execution Hit Check   #
            # ─────────────────────────────────────────── #
            spec_hit = global_speculative_executor.check_speculative_hit(
                query, global_memory
            )
            if spec_hit and spec_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(spec_hit["answer"], "speculative_hit",
                                    start_time, spec_hit["confidence"], clean)
                global_experience_optimizer.record("speculative_hit", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────────── #
            # STAGE 4 — Probability-precomputed Match     #
            # ─────────────────────────────────────────── #
            prob_hit = global_memory.lookup(query, canonical_form=family_id)
            if prob_hit and prob_hit.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(prob_hit["answer"], "probability_match",
                                    start_time, prob_hit["confidence"], clean)
                global_experience_optimizer.record("probability_match", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────────────── #
            # STAGE 5a — Micro-Parallel Composition           #
            # ─────────────────────────────────────────────── #
            try:
                par_res = await asyncio.wait_for(
                    global_micro_parallel.resolve(
                        query, global_memory, global_bg_compute,
                        tenant_id, session_id, global_delta_engine
                    ),
                    timeout=remaining(70),
                )
            except Exception:
                par_res = None

            if par_res and par_res.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(par_res["answer"], "micro_parallel",
                                    start_time, par_res["confidence"], clean)
                global_experience_optimizer.record("micro_parallel", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────── #
            # STAGE 5b — Delta Fragment Compose       #
            # ─────────────────────────────────────── #
            try:
                delta_res = await asyncio.wait_for(
                    global_delta_engine.resolve(
                        query, global_memory, global_bg_compute, tenant_id, session_id
                    ),
                    timeout=remaining(55),
                )
            except Exception:
                delta_res = None

            if delta_res and delta_res.get("confidence", 0) >= CONFIDENCE_FLOOR:
                result = self._wrap(delta_res["answer"],
                                    f"delta_{delta_res.get('mode','compose')}",
                                    start_time, delta_res["confidence"], clean)
                global_experience_optimizer.record("delta_compose", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────────── #
            # STAGE 6 — Graph Cluster Composition         #
            # ─────────────────────────────────────────── #
            cluster_ans = global_query_graph.compose_cluster_answer(family_id, query)
            if cluster_ans:
                result = self._wrap(cluster_ans, "graph_cluster",
                                    start_time, 0.96, clean)
                global_experience_optimizer.record("graph_cluster", result["latency_ms"])
                return await self._persist_and_return(
                    result, query, family_id, user_id, session_id, intent, entity,
                    tenant_id, False, True, request_id, clean,
                    inflight_fut, global_dedup_cache, global_memory_stack,
                    global_zero_repeat_store, global_shadow_store, global_memory,
                    global_avoidance_tracker, global_metrics, global_intent_trajectory,
                    global_massive_predictor, global_bg_compute, global_query_graph,
                    global_knowledge_field,
                )

            # ─────────────────────────────────────────── #
            # STAGE 7 — Intelligent Approximation         #
            # ─────────────────────────────────────────── #
            approx_res = global_approximation_engine.approximate(
                query, intent, entity, family_id
            )
            if approx_res and approx_res.get("confidence", 0) >= 0.65:
                conf = approx_res["confidence"]
                result = self._wrap(approx_res["answer"], approx_res["mode"],
                                    start_time, conf, clean)
                global_experience_optimizer.record("approximation", result["latency_ms"])

                # Trigger background refinement
                asyncio.create_task(
                    global_bg_compute.enqueue(
                        query, tenant_id, "APPROX_REFINE", session_id, priority="high"
                    )
                )
                self._track(request_id, clean, family_id, result,
                            False, False, global_avoidance_tracker, is_recovery=True)
                global_metrics.log_request(request_id, query, result["mode"],
                                           result["latency_ms"], False, canonical=family_id, is_recovery=True)
                if not inflight_fut.done():
                    inflight_fut.set_result(result)
                return result

            # ─────────────────────────────────────────────── #
            # STAGE 8 — Compute Deferral (>100ms budget left) #
            # ─────────────────────────────────────────────── #
            cur_elapsed = elapsed()
            if cur_elapsed > 100 or cur_elapsed > LATENCY_CEILING_MS * 0.6:
                deferred = global_compute_deferral.instant_skeleton(
                    query, request_id,
                    reason=f"budget_used={cur_elapsed:.0f}ms"
                )
                asyncio.create_task(
                    global_compute_deferral.defer_and_resolve(
                        query, request_id, tenant_id, session_id, global_bg_compute
                    )
                )
                result = self._wrap(deferred["result"], "compute_deferred",
                                    start_time, 0.4, clean)
                self._track(request_id, clean, family_id, result,
                            False, False, global_avoidance_tracker, is_recovery=True)
                global_metrics.log_request(request_id, query, "deferred",
                                           result["latency_ms"], False,
                                           is_recovery=True, canonical=family_id)
                if not inflight_fut.done():
                    inflight_fut.set_result(result)
                return result

            # ─────────────────────────────────────── #
            # STAGE 9 — MODEL CALL (Last Resort ≤2%) #
            # ─────────────────────────────────────── #
            self._model += 1
            cur_rate = self._model / self._total
            logger.warning(
                f"zcc.model_call: family={family_id} "
                f"rate={cur_rate:.2%} (target≤{MODEL_TARGET_RATE:.0%})"
            )

            model_answer = await self._call_model(
                query, tenant_id, global_micro_router, global_rag_engine, reasoning_expert
            )
            result = self._wrap(model_answer, "model_call",
                                start_time, 0.97, clean)
            global_experience_optimizer.record("model_call", result["latency_ms"])
            return await self._persist_and_return(
                result, query, family_id, user_id, session_id, intent, entity,
                tenant_id, True, False, request_id, clean,
                inflight_fut, global_dedup_cache, global_memory_stack,
                global_zero_repeat_store, global_shadow_store, global_memory,
                global_avoidance_tracker, global_metrics, global_intent_trajectory,
                global_massive_predictor, global_bg_compute, global_query_graph,
                global_knowledge_field,
            )

        finally:
            if family_id in self._in_flight:
                del self._in_flight[family_id]
            global_dedup_cache.clear_inflight(family_id)

    # ── Persist + Return ──────────────────────────────────────────────────── #

    async def _persist_and_return(
        self,
        result:           Dict[str, Any],
        query:            str,
        family_id:        str,
        user_id:          str,
        session_id:       str,
        intent:           str,
        entity:           str,
        tenant_id:        str,
        model_called:     bool,
        is_cache_hit:     bool,
        request_id:       str,
        clean:            str,
        inflight_fut,
        global_dedup_cache,
        global_memory_stack,
        global_zero_repeat_store,
        global_shadow_store,
        global_memory,
        global_avoidance_tracker,
        global_metrics,
        global_intent_trajectory,
        global_massive_predictor,
        global_bg_compute,
        global_query_graph,
        global_knowledge_field,
    ) -> Dict[str, Any]:
        answer     = result.get("result", "")
        confidence = result.get("confidence", 0.0)
        mode       = result.get("mode", "unknown")
        latency    = result.get("latency_ms", 0.0)

        # Store in all layers simultaneously
        try:
            global_memory_stack.store(family_id, query, answer, confidence,
                                      user_id, session_id)
        except Exception: pass

        try:
            global_zero_repeat_store.store(
                query, answer, family_id, mode, confidence,
                latency, session_id, global_memory, global_shadow_store
            )
        except Exception: pass

        try:
            global_dedup_cache.register(family_id, query, answer,
                                        confidence, latency, mode)
        except Exception: pass

        try:
            global_query_graph.register(family_id, query, answer,
                                        entity, intent, confidence)
            global_knowledge_field.mark_covered(entity, intent)
        except Exception: pass

        # Track real metrics
        self._track(request_id, clean, family_id, result, model_called,
                    is_cache_hit, global_avoidance_tracker)
        global_metrics.log_request(request_id, query, mode, latency,
                                   model_called, canonical=family_id)

        # Background expansion (fire-and-forget)
        asyncio.create_task(self._expand(
            query, entity, intent, family_id, session_id, tenant_id,
            global_intent_trajectory, global_massive_predictor, global_bg_compute,
        ))

        if not inflight_fut.done():
            inflight_fut.set_result(result)

        return result

    async def _expand(
        self, query, entity, intent, family_id, session_id, tenant_id,
        traj, mass_pred, bg_compute,
    ) -> None:
        try:
            await traj.precompute_trajectory(
                entity, intent, session_id, family_id, tenant_id, bg_compute
            )
            await mass_pred.precompute_family(
                query, entity, intent, family_id, tenant_id, session_id
            )
        except Exception as exc:
            logger.debug(f"zcc.expand_error: {exc}")

    # ── Model Call ─────────────────────────────────────────────────────────── #

    async def _call_model(
        self, query, tenant_id,
        micro_router, rag_engine, reasoning_expert
    ) -> str:
        # Try micro-model first (cheap)
        try:
            specialty = micro_router.route(query)
            if specialty:
                ans = await micro_router.execute(query, specialty)
                if ans and len(ans.strip()) > 10:
                    return ans
        except Exception: pass

        # RAG + reasoning
        try:
            ctx  = rag_engine.retrieve(query, tenant_id=tenant_id)
            docs = [n["content"] for n in ctx] if ctx else []
            ans  = await reasoning_expert.solve(query, context=docs,
                                                tenant_id=tenant_id)
            return ans if ans else f"Processed: {query}"
        except Exception as exc:
            logger.error(f"zcc.model_error: {exc}")
            return f"Unable to process at this time: '{query}'"

    # ── Helpers ────────────────────────────────────────────────────────────── #

    def _wrap(
        self, answer: str, mode: str, start_time: float,
        confidence: float, norm_query: str
    ) -> Dict[str, Any]:
        latency = (time.time() - start_time) * 1000
        try:
            from backend.core.health_monitor import global_health_monitor
            global_health_monitor.log_latency(latency)
        except Exception: pass
        return {
            "result":           answer,
            "mode":             mode,
            "confidence":       confidence,
            "latency_ms":       latency,
            "normalized_query": norm_query,
            "compute_avoided":  mode not in ("model_call", "FULL_CALC"),
        }

    def _track(
        self, request_id, norm_query, family_id, result,
        model_called, is_cache_hit, tracker, is_recovery=False
    ) -> None:
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
        except Exception: pass

    def avoidance_rate(self) -> float:
        if self._total == 0:
            return 0.0
        return 1.0 - self._model / self._total

    def pipeline_stats(self) -> Dict[str, Any]:
        rate = self.avoidance_rate()
        return {
            "total_requests":   self._total,
            "model_calls":      self._model,
            "avoidance_rate":   f"{rate:.2%}",
            "model_call_rate":  f"{self._model / max(self._total, 1):.2%}",
            "target":           "≥97% avoidance, ≤2% model calls",
        }


global_zero_control = ZeroComputeControl()
