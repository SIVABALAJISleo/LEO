"""
backend/shadow/shadow_worker.py
Shadow Execution Engine: Precomputes answers for predicted next queries.
"""
import logging
import asyncio
from backend.shadow.shadow_predictor import global_shadow_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.models.llm_loader import generate_response

logger = logging.getLogger(__name__)

class ShadowWorker:
    def __init__(self, shadow_store=global_shadow_store):
        self.shadow_store = shadow_store

    async def precompute_next_turns(self, query: str, session_id: str, tenant_id: str, workspace_id: str = "default"):
        """Background task: predicts next queries and precomputes their answers."""
        try:
            predictions = global_shadow_predictor.predict_next(query)
            logger.info("shadow_worker: predicted next queries = %s", predictions)
            
            loop = asyncio.get_event_loop()
            for p_query in predictions:
                # Skip if already in shadow store
                if self.shadow_store.lookup(p_query, session_id, tenant_id, workspace_id):
                    continue
                    
                logger.info("shadow_worker: precomputing for predicted query = '%s'", p_query)
                system_prompt = "You are a helpful AI assistant. Answer the predicted follow-up directly."
                answer = await loop.run_in_executor(
                    None, generate_response, p_query, 256, 0.7, system_prompt
                )
                
                self.shadow_store.save_shadow(
                    question=p_query,
                    answer=answer,
                    confidence=0.85,
                    session_id=session_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id
                )
        except Exception as exc:
            logger.error("shadow_worker: error during precomputation - %s", exc)

global_shadow_worker = ShadowWorker()