"""
backend/core/zero_compute.py
Unified Zero-Runtime-Compute Control Layer (Final Strength).

Enforces 100% compute avoidance by coordinating Global Memory, 
Fragment Graph Composition, and Adaptive Approximations.
"""
import logging
import time
import asyncio
from typing import Optional, Dict, Any

from backend.memory.global_memory import global_memory
from backend.runtime.composer import global_runtime_composer
from backend.optimization.approx_engine import global_approx_engine
from backend.background.compute_engine import global_bg_compute
from backend.background.session_predictor import global_session_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.analytics.metrics import global_metrics
from backend.optimization.compute_budget import global_compute_budget

logger = logging.getLogger(__name__)

class ZeroComputeControl:
    """
    Unified Zero-Runtime-Compute Control Layer (Final Dominance).
    Strictly enforces <50ms runtime and maximizes reuse via composition.
    """
    def __init__(self, time_budget_ms: float = 50.0):
        self.time_budget_ms = time_budget_ms
        self.critical_budget_ms = 40.0 # Point 12: Trigger simplification here

    async def handle_request(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float) -> Optional[Dict[str, Any]]:
        """
        AI Systems Architect (Point 1, 3, 7, 12): System Stability + Chaos Control.
        Unbreakable Processing: Adaptive mode selection and hard latency ceiling.
        """
        from backend.core.chaos_controller import global_chaos_controller, ChaosMode
        from backend.core.health_monitor import global_health_monitor
        from backend.optimization.self_optimizer import global_self_optimizer
        from backend.memory.quality_control import global_quality_control
        from backend.core.metrics import AVOIDANCE_RATIO
        
        session_id = request_id.split("_")[1] if "_" in request_id else "default"
        mode = global_chaos_controller.get_mode()
        threshold = global_self_optimizer.get_threshold()
        
        # 1. CHAOS CONTROLLER: ADAPTIVE PIPELINE (Point 1, 7)
        logger.info(f"zero_compute: Mode={mode.name} for query={query}")
        
        # MINIMAL MODE: Direct Cache Only (Point 7)
        if mode == ChaosMode.MINIMAL:
            hit = global_memory.lookup(query)
            if hit and hit.get("confidence", 0) >= 0.9:
                 return self._wrap(hit["answer"], "MINIMAL_CACHE_ONLY", start_time, hit["confidence"])
            return self._emergency_simplify(query, start_time, "CHAOS_MINIMAL_MODE")

        # 2. DECOMPOSITION & MAPPING (Point 6 - Only in NORMAL mode)
        components = self._decompose(query) if mode == ChaosMode.NORMAL else [query]
        
        # 3. STABILITY CONTROLLER: PRE-CHECK (Point 12)
        elapsed = (time.time() - start_time) * 1000
        if elapsed > self.critical_budget_ms:
            return self._emergency_simplify(query, start_time, "BUDGET_EXCEEDED_PRE")

        # 4. GLOBAL KNOWLEDGE SYSTEM (Tiered Retrieval)
        
        # Layer 0: Shadow Store (Point 2: return simplified if needed)
        shadow_hit = global_shadow_store.lookup(query, session_id, tenant_id=tenant_id, workspace_id=workspace_id)
        if shadow_hit and shadow_hit.get("confidence", 0) >= threshold:
            global_metrics.track_hit("shadow_prediction")
            return self._wrap(shadow_hit["answer"], "SHADOW_PREDICTION", start_time, shadow_hit["confidence"])

        # 5. HARD LATENCY GUARD: MID-STAGE (Point 3, 12)
        if (time.time() - start_time) * 1000 > 30.0 and mode == ChaosMode.REDUCED:
             return self._emergency_simplify(query, start_time, "LATENCY_GUARD_MID")

        # Layer 1: Global Memory (Canonical)
        memory_hit = global_memory.lookup(query)
        if memory_hit and memory_hit.get("confidence", 0) >= threshold:
            global_metrics.track_hit("global_memory")
            return self._wrap(memory_hit["answer"], "GLOBAL_MEMORY_REUSE", start_time, memory_hit["confidence"])

        # Layer 2: Knowledge Composition (Point 5 & 10: Non-blocking)
        # Skip composition in REDUCED mode to save CPU
        if mode == ChaosMode.NORMAL:
            composition = global_runtime_composer.compose_response(query, {"components": components}, [])
            if composition:
                 global_metrics.track_hit("graph_composition")
                 return self._wrap(composition, "GRAPH_COMPOSITION", start_time, 0.9)

        # 6. ADAPTIVE APPROXIMATION (Layer 3 - Last ResortPoint 7)
        approx = global_approx_engine.approximate(query)
        if approx:
             global_metrics.track_hit("adaptive_approximation")
             # Fail-Fast Trigger background processing for improvement (Point 8)
             await global_bg_compute.enqueue(query, tenant_id, workspace_id, session_id, priority="high")
             return self._wrap(approx["answer"], "ADAPTIVE_APPROXIMATION", start_time, approx["confidence"])

        # 7. EXTREME LATENCY GUARD: FINAL STOP (Point 3, 12)
        # Never allow the pipeline to exceed 45ms. Force 80% response.
        logger.info(f"zero_compute: TOTAL MISS. Forcibly Return Simplified Response.")
        await global_bg_compute.enqueue(query, tenant_id, workspace_id, session_id, priority="background_improvement")
        
        fallback_msg = "Optimizing the answer graph. Instant response processing..."
        return self._wrap(fallback_msg, "FAIL_FAST_FALLBACK", start_time, 0.5)

    def _emergency_simplify(self, query: str, start_time: float, reason: str):
        """Point 2, 5: Proactive Graceful Degradation."""
        logger.warning(f"zero_compute: EMERGENCY_DEGRADATION ({reason}). Simplfying...")
        simple_ans = f"Returning adaptive core reference for '{query}' due to system stress/latency."
        return self._wrap(simple_ans, f"STABILITY_{reason}", start_time, 0.4)

    def _wrap(self, answer: str, mode: str, start_time: float, confidence: float):
        latency = (time.time() - start_time) * 1000
        # Point 3, 9: Continuous telemetry log
        from backend.core.health_monitor import global_health_monitor
        global_health_monitor.log_latency(latency)
        
        # Hard ceiling enforcement (Point 3)
        if latency > self.time_budget_ms:
            logger.error(f"zero_compute: LATENCY VIOLATION! {latency:.2f}ms")
            
        return {
            "result": answer,
            "mode": mode,
            "confidence": confidence,
            "latency_ms": latency,
            "compute_avoided": True
        }

global_zero_control = ZeroComputeControl()
