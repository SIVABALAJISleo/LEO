import logging
import numpy as np
from typing import Optional, Dict, Any
from backend.core.database import SessionLocal, PrecomputedAnswer
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class ContinuousLearningEngine:
    """
    Stores high-confidence model answers in the durable Predictive store (PPE).
    Enables future queries with similar intent to bypass inference entirely.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()

    async def learn(self, query: str, answer: str, confidence: float, tenant_id: str = "default", workspace_id: str = "default"):
        """
        Evaluates and stores high-confidence results.
        """
        if confidence < 0.95:
            logger.info("skip_learning: confidence_too_low")
            return

        db = SessionLocal()
        try:
            # 1. Generate embedding for future vector lookup
            embedding = self.semantic_cache.model.encode([query])[0]
            
            # 2. Store in PrecomputedAnswer table (Layer 1 bypass)
            new_ans = PrecomputedAnswer(
                canonical_question=query,
                answer=answer,
                embedding=embedding.tobytes(),
                confidence=confidence,
                cluster_id=0, # Individual learning case
                tenant_id=tenant_id,
                workspace_id=workspace_id
            )
            db.add(new_ans)
            db.commit()
            logger.info(f"continuous_learning_applied: query_hash={self._get_hash(query)}")
        except Exception as e:
            logger.error(f"learning_failed: {e}")
            db.rollback()
        finally:
            db.close()

    def _get_hash(self, text: str) -> str:
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()

global_learning_engine = ContinuousLearningEngine()
