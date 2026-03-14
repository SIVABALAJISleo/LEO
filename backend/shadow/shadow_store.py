import logging
import json
import numpy as np
from typing import Optional, Dict, Any
from backend.core.database import SessionLocal, ShadowAnswer
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class ShadowAnswerStore:
    """
    Volatile but ultra-fast storage for Layer 0 (Shadow) predictions.
    Scoped by session_id to ensure low-collision, high-speed hits.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()

    def save_shadow(self, question: str, answer: str, confidence: float, session_id: str, tenant_id: str = "default"):
        db = SessionLocal()
        try:
            # Generate embedding for vector lookup
            embedding = self.semantic_cache.model.encode([question])[0]
            
            new_ans = ShadowAnswer(
                question=question,
                answer=answer,
                embedding=embedding.tobytes(),
                confidence=confidence,
                session_id=session_id,
                tenant_id=tenant_id
            )
            db.add(new_ans)
            db.commit()
            logger.info(f"shadow_answer_stored: {question} [session={session_id}]")
        except Exception as e:
            logger.error(f"save_shadow_answer_error: {e}")
            db.rollback()
        finally:
            db.close()

    def lookup(self, query: str, session_id: str, tenant_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Ultra-fast lookup scoped to the active session.
        """
        db = SessionLocal()
        try:
            # 1. Broad fetch for the session (limiting search space to active turn context)
            candidates = db.query(ShadowAnswer).filter(
                ShadowAnswer.tenant_id == tenant_id,
                ShadowAnswer.session_id == session_id
            ).all()
            
            if not candidates:
                return None
                
            query_embedding = self.semantic_cache.model.encode([query])[0]
            
            best_match = None
            max_sim = 0
            
            for c in candidates:
                c_emb = np.frombuffer(c.embedding, dtype='float32')
                sim = np.dot(query_embedding, c_emb)
                if sim > max_sim:
                    max_sim = sim
                    best_match = c
            
            if max_sim > 0.90: # Slightly lower threshold than PPE for conversational variations
                logger.info(f"shadow_store_hit: score={max_sim} session={session_id}")
                return {
                    "answer": best_match.answer,
                    "confidence": max_sim,
                    "source": "ShadowEngine"
                }
        except Exception as e:
            logger.error(f"shadow_lookup_error: {e}")
        finally:
            db.close()
        return None

global_shadow_store = ShadowAnswerStore()
