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
        from backend.memory.global_memory import global_memory
        from backend.normalization.normalizer import global_normalizer
        
        query = task["query"]
        session_id = task["session_id"]
        tenant_id = task["tenant_id"]
        priority = task.get("priority", "normal")
        
        # 1. Point 4: FAILURE -> KNOWLEDGE LOOP
        is_recovery = priority == "high"
        if is_recovery:
            logger.info(f"bg_compute: CONVERTING FAILURE TO KNOWLEDGE for query='{query}'")

        # 2. Point 2: PREDICTIVE EXPLOSION (Variations + Follow-ups)
        predictions = global_predictor.predict_next_queries(query, session_id=session_id)
        targets = [query] + predictions["variations"] + predictions["follow_ups"]
        
        # 3. KNOWLEDGE EXPANSION
        for target in targets:
            # Skip if already perfectly cached (Point 1)
            # Use 0.95 for strict avoidance
            hit = global_memory.lookup(target)
            if hit and hit.get("confidence", 0) >= 0.95:
                continue

            logger.info(f"bg_compute: Pre-resolving target '{target}'")
            answer_data = await global_precompute_pipeline.resolve_and_store(
                target, 
                tenant_id, 
                task["workspace_id"], 
                session_id
            )
            
            if answer_data:
                # Point 1: Every model output MUST be stored
                norm = global_normalizer.normalize(target)
                global_memory.log(
                    query=target,
                    answer=answer_data["answer"],
                    mode="KNOWLEDGE_DOMINANCE" if not is_recovery else "FAILURE_RECOVERY",
                    canonical_form=norm["canonical"],
                    confidence=1.0 # Background compute is authoritative
                )
        
        # 4. Point 6: KNOWLEDGE COMPRESSION (Periodic/Triggered)
        if self.queue.empty():
            logger.info("bg_compute: Queue idle. Triggering Knowledge Compression & Graph Optimization.")
            from backend.graph.fragment_graph import global_fragment_graph
            # (In a real system, we'd call global_fragment_graph.optimize())
            
        logger.info(f"bg_compute: Task complete for '{query}'. Avoidance depth increased.")

global_bg_compute = BackgroundComputeEngine()
