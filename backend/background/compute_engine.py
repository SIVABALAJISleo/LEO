"""
backend/background/compute_engine.py
Main Background Intelligence Engine (Upgraded).

Continuously processes unknown queries, generates answers & variations, 
and expands the Knowledge Composition Graph.
"""
import asyncio
import logging
from typing import Dict, Any, List
from backend.analytics.metrics import global_metrics
from backend.shadow.shadow_store import global_shadow_store
from backend.predictive.predictor import global_predictor
from backend.learning.answer_store import global_learning_engine

logger = logging.getLogger(__name__)

class BackgroundComputeEngine:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def enqueue(self, query: str, tenant_id: str, workspace_id: str, session_id: str, priority: str = "normal"):
        """Enqueues a query for background processing."""
        await self.queue.put({
            "query": query,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "session_id": session_id,
            "priority": priority
        })
        global_metrics.track_hit("bg_enqueue")
        logger.info(f"bg_compute: Enqueued query='{query}' [priority={priority}]")

    async def run(self):
        """Main worker loop."""
        self.running = True
        logger.info("bg_compute: Engine started.")
        
        while self.running:
            task = await self.queue.get()
            try:
                await self._process_task(task)
            except Exception as e:
                logger.error(f"bg_compute: Task failed - {e}")
            finally:
                self.queue.task_done()

    async def _process_task(self, task: Dict[str, Any]):
        from backend.background.precompute_pipeline import global_precompute_pipeline
        from backend.memory.failure_store import global_failure_store
        from backend.memory.quality_control import global_quality_control
        
        query = task["query"]
        session_id = task["session_id"]
        tenant_id = task["tenant_id"]
        priority = task.get("priority", "normal")
        
        # 1. FAILURE INTELLIGENCE & RECOVERY (Point 8, 11)
        # Prioritize background improvement for failed/degraded queries
        if priority in ["high", "background_improvement"]:
            logger.info(f"bg_compute: RECOVERY MODE for '{query}' [Priority={priority}]")
            
        # 2. VARIATION EXPLOSION (Point 3)
        # Generate variations for proactive caching
        prediction_count = 12 if priority != "background_improvement" else 5
        variations = global_predictor.predict_next_queries(query, count=prediction_count)
        
        # 3. RESOLUTION & LEARNING LOOP (Point 8)
        targets = list(set([query] + variations))
        for target in targets:
            logger.info(f"bg_compute: Resolving and Stabilizing target '{target}'")
            
            # Heavy background resolution
            answer_data = await global_precompute_pipeline.resolve_and_store(
                target, 
                tenant_id, 
                task["workspace_id"], 
                session_id
            )
            
            if answer_data:
                # 4. Global Memory Update (Point 4)
                from backend.normalization.normalizer import global_normalizer
                from backend.memory.global_memory import global_memory
                norm = global_normalizer.normalize(target)
                global_memory.log(
                    query=target,
                    answer=answer_data["answer"],
                    mode="BACKGROUND_STABILITY_RECOVERY",
                    canonical_form=norm["canonical"],
                    confidence=1.0
                )
                
                # Signal success for recovery
                if priority == "background_improvement":
                     logger.info(f"bg_compute: RECOVERY SUCCESS for '{target}'")
            
        logger.info(f"bg_compute: Stability Recovery Loop completed for '{query}'")

global_bg_compute = BackgroundComputeEngine()
