import asyncio
import logging
from backend.shadow.shadow_predictor import global_shadow_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.intelligence.reasoning import reasoning_expert

logger = logging.getLogger(__name__)

class ShadowWorker:
    """
    Processes predicted queries in the background during active sessions.
    Stores results in the Shadow Answer Store (Layer 0).
    """
    def __init__(self, shadow_store=global_shadow_store):
        self.shadow_store = shadow_store
        self.active_tasks = {}

    async def precompute_next_turns(self, query: str, session_id: str, tenant_id: str):
        """
        Background task triggered after a primary response is delivered.
        """
        try:
            # 1. PREDICT NEXT QUERIES
            predictions = global_shadow_predictor.predict_next(query)
            
            for p_query in predictions:
                logger.info(f"shadow_predictive_inference: {p_query} [session={session_id}]")
                # 2. GENERATE ANSWER (Layer 0 Shadow Inference)
                result = await reasoning_expert.solve(p_query, tenant_id=tenant_id, session_id=session_id)
                
                # 3. STORE IN SHADOW STORE
                if self.shadow_store:
                    self.shadow_store.save_shadow(
                        question=p_query,
                        answer=result["answer"],
                        confidence=result.get("confidence", 0.9),
                        session_id=session_id,
                        tenant_id=tenant_id
                    )
        except Exception as e:
            logger.error(f"shadow_worker_error: {e}")

global_shadow_worker = ShadowWorker()
