"""
backend/background/compute_engine.py
Main Background Compute Engine for Zero Runtime Compute.

Processes enqueued queries, generates precomputed answers,
and feeds the predictive store.
"""
import asyncio
import logging
from typing import Dict, Any, List
from backend.analytics.metrics import global_metrics
from backend.shadow.shadow_store import global_shadow_store

logger = logging.getLogger(__name__)

class BackgroundComputeEngine:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def enqueue(self, query: str, tenant_id: str, workspace_id: str, session_id: str):
        """Enqueues a query for background processing."""
        await self.queue.put({
            "query": query,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "session_id": session_id
        })
        global_metrics.track_unknown_event("micro_compute") # Tracking as background task
        logger.info(f"bg_compute: Enqueued query='{query}'")

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
        from backend.background.predictor import global_predictor
        from backend.intelligence.domain_expander import global_domain_expander
        from backend.intelligence.decomposer import global_decomposer

        query = task["query"]
        logger.info(f"bg_compute: Processing query='{query}'")
        
        # 1. Expand query into variations and next-likely questions
        variations = await global_predictor.predict_variations(query)
        
        # 1.1 Proactive Session Prediction (Phase 27)
        from backend.background.session_predictor import global_session_predictor
        session_predictions = await global_session_predictor.predict_next_steps(task["session_id"])
        
        # 2. Decompose for domain expansion
        decomposed = global_decomposer.decompose(query)
        
        # 3. Trigger domain expansion for unknown topics
        await global_domain_expander.expand_and_store(query, decomposed, task["tenant_id"])
        
        # 4. Run high-precision refinement (Phase 38 - Background Completion)
        # We resolve the query and its variations to 100% precision 
        # to replace any runtime approximations.
        targets = [query] + variations + session_predictions
        for target in targets:
            answer_data = await global_precompute_pipeline.resolve_and_store(
                target, 
                task["tenant_id"], 
                task["workspace_id"], 
                task["session_id"]
            )
            
            # 5. STORAGE SYNCHRONIZATION
            if answer_data:
                 # Update all stores to replace any "Good Enough" sync results
                 global_shadow_store.register(target, answer_data["answer"], task["session_id"], tenant_id=task["tenant_id"])
                 
                 from backend.intelligence.delta_engine import global_delta_engine_v2
                 global_delta_engine_v2.register_answer(target, answer_data["answer"])
                 
                 from backend.answers.semantic_canonical import global_semantic_canonical
                 global_semantic_canonical.register(target, answer_data["answer"], None, task["tenant_id"])
            
        logger.info(f"bg_compute: Finished completion for '{query}' and {len(variations+session_predictions)} variations.")

global_bg_compute = BackgroundComputeEngine()
