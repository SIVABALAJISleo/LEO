import logging
import json
import numpy as np
from typing import Optional, Dict, Any
from backend.core.database import SessionLocal, PrecomputedAnswer
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class PredictiveAnswerStore:
    """
    Durable storage and fast lookup for Layer 1 (Predictive) answers.
    Uses vector similarity for high-recall retrieves.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()

    def save_answer(self, question: str, answer: str, confidence: float, cluster_id: int = 0, tenant_id: str = "default", workspace_id: str = "default"):
        db = SessionLocal()
        try:
            # Generate embedding for vector lookup
            embedding = np.asarray(self.semantic_cache.model.encode([question])[0])
            
            new_ans = PrecomputedAnswer(
                canonical_question=question,
                answer=answer,
                embedding=embedding.tobytes(),
                confidence=confidence,
                cluster_id=cluster_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id
            )
            db.add(new_ans)
            db.commit()
            logger.info(f"predictive_answer_stored: {question}")
        except Exception as e:
            logger.error(f"save_predictive_answer_error: {e}")
            db.rollback()
        finally:
            db.close()

    def lookup(self, query: str, tenant_id: str = "default", workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Fast lookup using vector similarity on precomputed answers.
        """
        db = SessionLocal()
        try:
            # 1. Broad fetch for the workspace/tenant
            candidates = db.query(PrecomputedAnswer).filter(
                PrecomputedAnswer.tenant_id == tenant_id,
                PrecomputedAnswer.workspace_id == workspace_id
            ).all()
            if not candidates:
                return None
                
            # 2. Vector search (Small scale example, use pgvector in production)
            query_embedding = np.asarray(self.semantic_cache.model.encode([query])[0])
            
            best_match = None
            max_sim = 0
            
            for c in candidates:
                # Use bytes() to ensure we have a bytes object for frombuffer
                c_emb = np.frombuffer(bytes(c.embedding), dtype='float32') # type: ignore
                # Ensure dot product is float
                sim = float(np.dot(query_embedding, c_emb))
                if sim > max_sim:
                    max_sim = sim
                    best_match = c
            
            if max_sim > 0.95: # High confidence threshold for Layer 1
                logger.info(f"predictive_store_hit: score={max_sim}")
                return {
                    "answer": best_match.answer if best_match else "",
                    "confidence": max_sim,
                    "source": "PPE"
                }
        except Exception as e:
            logger.error(f"predictive_lookup_error: {e}")
        finally:
            db.close()
        return None

global_predictive_store = PredictiveAnswerStore()
