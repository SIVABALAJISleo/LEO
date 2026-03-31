"""
backend/background/session_predictor.py
Session-Aware Query Prediction Engine (Upgraded).

Tracks user query history, predicts next 3-10 interactions, 
and triggers proactive background precomputation into ShadowStore.
"""
import logging
import asyncio
from typing import List, Dict
from collections import deque
from backend.predictive.predictor import global_predictor
from backend.shadow.shadow_store import global_shadow_store

logger = logging.getLogger(__name__)

class SessionPredictor:
    def __init__(self, history_limit: int = 10):
        # session_id -> deque of recent queries
        self.session_histories: Dict[str, deque] = {}
        self.history_limit = history_limit

    def track_query(self, session_id: str, query: str):
        """Adds a query and triggers predictive background expansion."""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = deque(maxlen=self.history_limit)
        
        self.session_histories[session_id].append(query)
        global_predictor.log_query(session_id, query) # Sync with global predictor
        
        # Trigger Background Prediction (Async)
        asyncio.create_task(self._expand_and_precompute(session_id, query))

    async def _expand_and_precompute(self, session_id: str, query: str):
        """
        AI Systems Architect (Point 8): Predictive Session Intelligence.
        Generates predictions and enqueues them for background compute.
        """
        # 1. Rule-based predictions (Point 2) - Instant
        rule_preds = global_predictor.predict_next_queries(query, count=6)
        
        # 2. Sequence-based predictions (Point 8): Predict next queries based on session
        seq_preds = await self.predict_next_steps(session_id)
        
        all_preds = list(set(rule_preds + seq_preds))[:10]
        logger.info(f"session_predictor: Enqueuing {len(all_preds)} session-proactive predictions.")
        
        from backend.background.compute_engine import global_bg_compute
        for p in all_preds:
            # Point 10: Continuous Background Intelligence Engine
            # Process unknown queries and generate answers without user waiting
            await global_bg_compute.enqueue(p, "default", "default", session_id, priority="high")

    async def predict_next_steps(self, session_id: str) -> List[str]:
        """
        Analyzes session history and predicts the next 3-5 likely queries.
        Uses LLM logic in the background.
        """
        history = self.session_histories.get(session_id, [])
        if not history:
            return []
            
        from backend.models.llm_loader import generate_response
        
        history_str = " -> ".join(list(history)[-5:])
        prompt = (
            f"Based on the following query sequence: '{history_str}', "
            "predict the next 5 most likely questions the user will ask. "
            "Output ONLY a comma-separated list of queries."
        )
        
        system_prompt = "You are a session intent predictor. Output ONLY a comma-separated list of questions."
        
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, lambda: generate_response(prompt, 256, 0.7, system_prompt)
            )
            
            predictions = [p.strip() for p in str(result).replace('\n', ',').split(',') if p.strip() and len(p) > 5]
            return predictions[:5]
        except Exception as e:
            logger.error(f"session_predictor fallback: {e}")
            return []

global_session_predictor = SessionPredictor()
