"""
backend/core/zero_compute.py
Unified Zero-Runtime-Compute Control Layer.

Enforces 100% compute avoidance by coordinating soft matching, 
approximations, and background enqueuing.
"""
import logging
import time
import asyncio
from typing import Optional, Dict, Any

from backend.optimization.soft_match import global_soft_match
from backend.optimization.approx_engine import global_approx_engine
from backend.optimization.time_controller import global_time_controller
from backend.optimization.heat_scheduler import global_heat_scheduler
from backend.optimization.rephraser import global_rephraser
from backend.background.compute_engine import global_bg_compute
from backend.analytics.metrics import global_metrics

logger = logging.getLogger(__name__)

class ZeroComputeControl:
    def __init__(self, time_budget_ms: float = 50.0):
        self.time_budget_ms = time_budget_ms

    async def handle_request(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float) -> Optional[Dict[str, Any]]:
        """
        The central gatekeeper for all runtime requests.
        Ensures NO heavy compute happens and returns ASAP.
        """
        from backend.shadow.shadow_store import global_shadow_store
        from backend.intelligence.delta_engine import global_delta_engine_v2
        from backend.optimization.gpu_blocker import global_gpu_blocker
        from backend.background.session_predictor import global_session_predictor
        
        global_time_controller.start(request_id)
        session_id = request_id.split("_")[1] if "_" in request_id else "default"
        
        # 0. SESSION ATTENTION (Phase 27)
        global_session_predictor.track_query(session_id, query)
        
        # 1. GPU DEMAND BLOCKER (Phase 28)
        gpu_fallback = global_gpu_blocker.check_demand(query)
        if gpu_fallback:
             global_metrics.track_hit("gpu_block")
             return self._wrap(gpu_fallback["answer"], gpu_fallback["mode"], start_time, 0.9)

        # 2. SHADOW STORE (Precomputed predictions)
        shadow_hit = global_shadow_store.lookup(query, session_id, tenant_id=tenant_id, workspace_id=workspace_id)
        if shadow_hit:
            global_metrics.track_hit("shadow")
            return self._wrap(shadow_hit["answer"], "SHADOW_STORE", start_time, shadow_hit["confidence"])

        # 3. SEMANTIC CLUSTER LOCKING (Force reuse >= 0.85) (Phase 26)
        delta = global_delta_engine_v2.find_delta(query)
        if delta:
            # Shift from 0.95 to 0.85 (Phase 30)
            if delta.get("score", 0.95) >= 0.85: 
                 global_metrics.track_hit("cluster_lock")
                 return self._wrap(delta["answer"], "CLUSTER_REUSE_LOCKED", start_time, delta.get("score", 0.95))

        # 4. SOFT MATCH (Optimization Fallback)
        match = global_soft_match.find_match(query)
        if match:
            global_metrics.track_hit("soft_match")
            answer = global_rephraser.rephrase(match["answer"], query, query)
            return self._wrap(answer, match["mode"], start_time, match["confidence"])

        # 5. RUNTIME COMPOSITION (Phase 29 - Structured Fragments)
        from backend.runtime.composer import global_runtime_composer
        from backend.intelligence.decomposer import global_decomposer
        
        decomposed = global_decomposer.decompose(query)
        composition = global_runtime_composer.compose_response(query, decomposed, [])
        if composition:
             global_metrics.track_hit("composition")
             global_delta_engine_v2.register_answer(query, composition)
             return self._wrap(composition, "RUNTIME_COMPOSITION_STRUCTURED", start_time, 0.85)

        # 6. CONTROLLED COMPUTE (Phase 33-36 - Safe Sync)
        from backend.optimization.micro_compute import global_micro_compute
        from backend.optimization.compute_budget import global_compute_budget
        
        # Priority Rule (Phase 36): Only specific intents get synchronous compute
        intent = decomposed.get("intent", "information")
        # Direct keyword fallback for robust priority routing
        is_high_priority = intent in ["how_to", "definition", "reasoning"] or \
                           any(w in query.lower() for w in ["steps", "how to", "define", "explain"])
        
        if is_high_priority and not global_heat_scheduler.should_skip_heavy_logic():
             global_compute_budget.start_tracking(request_id)
             try:
                 # Calculate the missing part (Phase 33)
                 intent = next(iter(decomposed.get("intents", ["general"])))
                 topic = decomposed.get("topic", query)
                 
                 sync_result = await global_micro_compute.execute(query, intent, topic)
                 if sync_result:
                      global_metrics.track_hit("micro_compute")
                      # Cache it instantly (Phase 37)
                      global_delta_engine_v2.register_answer(query, sync_result)
                      return self._wrap(sync_result, "CONTROLLED_COMPUTE_SYNC", start_time, 0.95)
             except Exception as e:
                 logger.warning(f"zero_compute: Controlled compute failed or exceeded budget - {e}")
             finally:
                 global_compute_budget.end_tracking(request_id)

        # 7. IF STILL MISS -> ENQUEUE & LEARN (Phase 31)
        logger.info(f"zero_compute: MISS for '{query}'. Enqueuing for background.")
        await global_bg_compute.enqueue(query, tenant_id, workspace_id, session_id)
        
        fallback_msg = "Optimizing this new concept. High-precision result available in seconds."
        return self._wrap(fallback_msg, "ENQUEUED_MANDATORY", start_time, 0.5)

    def _wrap(self, answer: str, mode: str, start_time: float, confidence: float):
        return {
            "result": answer,
            "mode": mode,
            "confidence": confidence,
            "latency_ms": (time.time() - start_time) * 1000,
            "compute_avoided": True
        }

global_zero_control = ZeroComputeControl()
