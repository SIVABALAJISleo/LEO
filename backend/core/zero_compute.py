"""
backend/core/zero_compute.py
Unified Zero-Runtime-Compute Control Layer (Final Strength).

Enforces 100% compute avoidance by coordinating Global Memory, 
Fragment Graph Composition, and Adaptive Approximations.
"""
import logging
import time
import asyncio
from typing import Optional, Dict, Any, Set

from backend.memory.global_memory import global_memory
from backend.runtime.composer import global_runtime_composer
from backend.optimization.approx_engine import global_approx_engine
from backend.background.compute_engine import global_bg_compute
from backend.background.session_predictor import global_session_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.analytics.metrics import global_metrics
from orchestration.chaos_containment import global_chaos_containment
from backend.intelligence.reasoning import reasoning_expert
from backend.intelligence.rag import global_rag_engine
from backend.micro_models.router import global_micro_router

from backend.normalization.normalizer import global_normalizer

logger = logging.getLogger(__name__)

class ZeroComputeControl:
    """
    ULTRA HIT-RATE ENGINE (CIS++).
    Point 1-10: Maximize reuse and eliminate recompute.
    """
    def __init__(self):
        self.time_budget_ms = 200.0
        self.in_flight: Dict[str, asyncio.Future] = {}
        self.hot_families: Set[str] = set() # Point 5: Top 1% in RAM
        self.partial_cache: Dict[str, str] = {} # Point 3: Partial Answer components

    async def handle_request(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float) -> Optional[Dict[str, Any]]:
        """
        MISSION: Achieve 97-98% Compute Avoidance (Ultra-Hit Rate).
        Probability Router -> Family Mapping -> Top-K Match -> Partial Composition
        """
        # 1. FAMILY MAPPING (Point 2)
        norm_data = global_normalizer.normalize(query)
        family_id = norm_data["family_id"]
        clean_norm = norm_data["clean"]
        session_id = request_id.split("_")[1] if "_" in request_id else "default"

        def get_timeout(cap_ms: float) -> float:
            elapsed = (time.time() - start_time) * 1000
            return max(min(self.time_budget_ms - elapsed, cap_ms), 1.0) / 1000.0

        # 2. PROBABILITY ROUTER (Point 4)
        # Skip deep layers if family is hot/confirmed
        is_high_prob = family_id in self.hot_families
        
        # 3. CONCURRENCY DEDUP
        if family_id in self.in_flight:
            try:
                pending_res = await asyncio.wait_for(self.in_flight[family_id], timeout=get_timeout(1000))
                return self._wrap(pending_res["result"], "reuse", start_time, 1.0, clean_norm)
            except Exception: pass

        self.in_flight[family_id] = asyncio.get_event_loop().create_future()
        
        try:
            # ULTRA HIT-RATE ENGINE (Point 1)
            # Tier 1: Exact Family Match (RAM/Shadow Store)
            try:
                shadow_hit = await asyncio.wait_for(
                    asyncio.to_thread(global_shadow_store.lookup, family_id, session_id),
                    timeout=get_timeout(40)
                )
                if shadow_hit and shadow_hit.get("confidence", 0) >= 0.90:
                    self.hot_families.add(family_id) # Learn hot query
                    res = self._wrap(shadow_hit["answer"], "memory_exact", start_time, 1.0, clean_norm)
                    global_metrics.log_request(request_id, query, "memory_exact", res["latency_ms"], False, canonical=family_id)
                    if not self.in_flight[family_id].done(): self.in_flight[family_id].set_result(res)
                    return res
            except Exception: pass

            # Tier 2: Top-K Semantic Match (k=3, Point 1)
            try:
                # Dynamic Threshold Logic
                threshold = 0.92 if is_high_prob else 0.85
                top_k_hits = await asyncio.wait_for(
                    asyncio.to_thread(global_memory.search, query, k=3, threshold=threshold),
                    timeout=get_timeout(100)
                )
                if top_k_hits:
                    best_match = top_k_hits[0]
                    # PARTIAL ANSWER CACHE COMPO (Point 3)
                    final_ans = best_match["answer"]
                    if len(top_k_hits) > 1 and "explain" in query.lower():
                        final_ans += "\n\nSupplementary context: " + top_k_hits[1]["answer"]
                        
                    res = self._wrap(final_ans, "memory_top_k", start_time, best_match["confidence"], clean_norm)
                    global_metrics.log_request(request_id, query, "memory_top_k", res["latency_ms"], False, canonical=family_id)
                    if not self.in_flight[family_id].done(): self.in_flight[family_id].set_result(res)
                    return res
            except Exception: pass

            # Tier 3: Adaptive Prediction (Point 6)
            try:
                predict_hit = await asyncio.wait_for(self._predictive_attention(query, session_id), timeout=get_timeout(50))
                if predict_hit:
                    res = self._wrap(predict_hit["answer"], "prediction", start_time, 0.90, clean_norm)
                    global_metrics.log_request(request_id, query, "prediction", res["latency_ms"], False, is_prediction_hit=True, canonical=family_id)
                    if not self.in_flight[family_id].done(): self.in_flight[family_id].set_result(res)
                    return res
            except Exception: pass

            # FALLBACK ELIMINATION (Point 9 & 10)
            res = self._proactive_instant_skeleton(query, start_time, "KNOWLEDGE_MATURATION")
            global_metrics.log_request(request_id, query, "approximation_skeleton", res["latency_ms"], False, is_recovery=True, canonical=family_id)
            asyncio.create_task(global_bg_compute.enqueue(query, tenant_id, workspace_id, session_id, priority="high"))
            
            if not self.in_flight[family_id].done(): self.in_flight[family_id].set_result(res)
            return res
        finally:
            if family_id in self.in_flight:
                del self.in_flight[family_id]

    def _local_attention(self, query: str) -> Dict[str, Any]:
        """Layer 1: extract intent/keywords."""
        q_clean = query.lower().strip()
        keywords = [w for w in q_clean.split() if len(w) > 3]
        intent = "composition" if "," in query or " and " in q_clean else "lookup"
        return {"keywords": keywords, "intent": intent, "parts": self._decompose(query)}

    async def _predictive_attention(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Layer 3: match predicted/precomputed queries."""
        from backend.predictive.predictor import global_predictor
        predictions = global_predictor.predict_next_queries(query, session_id)
        targets = predictions["variations"] + predictions["follow_ups"]
        
        for target in targets:
            hit = global_memory.lookup(target)
            if hit and hit.get("confidence", 0) >= 0.90:
                return hit
        return None

    async def _compute_collapse(self, query: str, local_ctx: Dict[str, Any], tenant_id: str) -> Optional[Dict[str, Any]]:
        """MICRO-DELTA COMPUTE (Point 5)."""
        components = local_ctx["parts"]
        if len(components) <= 1: return None 
        
        try:
            loop = asyncio.get_event_loop()
            context_nodes = await loop.run_in_executor(None, global_rag_engine.retrieve, query, tenant_id, 3, True)
            fragments = [n["content"] for n in context_nodes] if context_nodes else []
            composition, missing = global_runtime_composer.compose_response(query, {"components": components}, fragments)
            
            if missing:
                delta_results = []
                for m in missing:
                    specialty = global_micro_router.route(m)
                    if specialty:
                        delta_ans = await global_micro_router.execute(m, specialty)
                        delta_results.append(delta_ans)
                if delta_results:
                    composition = (composition or "") + ("\n\n" if composition else "") + "\n\n".join(delta_results)
            
            if composition: return {"answer": composition}
            return None
        except Exception: return None

    def _proactive_instant_skeleton(self, query: str, start_time: float, reason: str):
        """Standard CIS++ response for new knowledge paths."""
        insight = f"Analyzing intelligence for: '{query}'. Contextual metadata identified. Standardizing authoritative cache entries in background..."
        return self._wrap(insight, "skeleton", start_time, 0.4, query)

    def _decompose(self, query: str) -> list:
        parts = [p.strip() for p in query.replace(" and ", ",").replace(" plus ", ",").split(",") if p.strip()]
        return parts if parts else [query]

    def _wrap(self, answer: str, mode: str, start_time: float, confidence: float, norm_query: str):
        latency = (time.time() - start_time) * 1000
        from backend.core.health_monitor import global_health_monitor
        global_health_monitor.log_latency(latency)
        
        return {
            "result": answer,
            "mode": mode,
            "confidence": confidence,
            "latency_ms": latency,
            "normalized_query": norm_query,
            "compute_avoided": mode != "model"
        }

global_zero_control = ZeroComputeControl()

global_zero_control = ZeroComputeControl()
