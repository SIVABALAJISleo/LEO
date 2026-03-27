"""
backend/background/session_predictor.py
Session-Aware Query Prediction Engine.

Tracks user query history and predicts the next 3-5 likely interactions 
to trigger proactive background compute.
"""
import logging
from typing import List, Dict
from collections import deque

logger = logging.getLogger(__name__)

class SessionPredictor:
    def __init__(self, history_limit: int = 10):
        # session_id -> deque of recent queries
        self.session_histories: Dict[str, deque] = {}
        self.history_limit = history_limit

    def track_query(self, session_id: str, query: str):
        """Adds a query to the session history."""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = deque(maxlen=self.history_limit)
        self.session_histories[session_id].append(query)

    async def predict_next_steps(self, session_id: str) -> List[str]:
        """
        Analyzes session history and predicts the next 3-5 likely queries.
        Uses LLM logic in the background.
        """
        history = self.session_histories.get(session_id, [])
        if not history:
            return []
            
        logger.info(f"session_predictor: Predicting next steps for session '{session_id}' (history_len={len(history)})")
        
        from backend.models.llm_loader import generate_response
        import asyncio
        
        history_str = " -> ".join(list(history)[-5:])
        prompt = (
            f"Based on the following query sequence: '{history_str}', "
            "predict the next 5 most likely questions the user will ask. "
            "Output ONLY a comma-separated list of queries."
        )
        
        system_prompt = "You are a session intent predictor. Output ONLY a comma-separated list of questions."
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, generate_response, prompt, 256, 0.7, system_prompt
            )
            
            predictions = [p.strip() for p in result.replace('\n', ',').split(',') if p.strip() and len(p) > 5]
            logger.info(f"session_predictor: Predicted {len(predictions)} future queries.")
            return predictions[:5]
            
        except Exception as e:
            logger.error(f"session_predictor: Prediction failed - {e}")
            return []

global_session_predictor = SessionPredictor()
