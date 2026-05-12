import logging
import numpy as np
from typing import Optional, Dict, Any
from backend.core.database import SessionLocal, ShadowAnswer
from backend.intelligence.router import SemanticCache

logger = logging.getLogger(__name__)

class ShadowAnswerStore:
    """
    Volatile but ultra-fast storage for Layer 0 (Shadow) predictions.
    Scoped by session_id to ensure low-collision, high-speed hits.

    Upgraded: maintains an in-memory RAM cache (family_id → answer)
    for sub-millisecond exact lookups (TriAttention Tier 1).
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()
        # RAM cache: {family_id: {answer, confidence, mode, session_id}}
        self._ram_cache: Dict[str, Dict[str, Any]] = {}

    def store(
        self,
        family_id: str,
        session_id: str,
        answer: str,
        confidence: float,
        mode: str = "computed",
    ) -> None:
        """
        Stores a computed answer to the in-memory RAM cache keyed by family_id.
        Used by zero_repeat_store for instant Tier-1 lookups.
        """
        self._ram_cache[family_id] = {
            "answer": answer,
            "confidence": confidence,
            "mode": mode,
            "session_id": session_id,
        }
        logger.debug(
            f"shadow_store.ram_stored: family={family_id} "
            f"confidence={confidence:.3f}"
        )

    def register(self, question: str, answer: str, session_id: str, tenant_id: str = "default", workspace_id: str = "default"):
        return self.save_shadow(question, answer, 1.0, session_id, tenant_id, workspace_id)

    def save_shadow(self, question: str, answer: str, confidence: float, session_id: str, tenant_id: str = "default", workspace_id: str = "default"):
        db = SessionLocal()
        try:
            embedding = np.asarray(self.semantic_cache.model.encode([question])[0])
            new_ans = ShadowAnswer(
                question=question,
                answer=answer,
                embedding=embedding.tobytes(),
                confidence=confidence,
                session_id=session_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id
            )
            db.add(new_ans)
            db.commit()
            logger.info(f"shadow_answer_stored: {question} [session={session_id}]")
        except Exception as e:
            logger.error(f"save_shadow_answer_error: {e}")
            db.rollback()
        finally:
            db.close()

    def lookup(self, query: str, session_id: str, tenant_id: str = "default", workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Ultra-fast lookup — checks RAM cache first (Tier-1 exact match by family_id),
        then falls back to DB semantic search.
        """
        # 1. RAM cache — exact family_id match (sub-millisecond)
        if query in self._ram_cache:
            entry = self._ram_cache[query]
            logger.info(
                f"shadow_store.ram_hit: family={query} "
                f"confidence={entry['confidence']:.3f}"
            )
            return entry

        # 2. DB semantic lookup (session-scoped)
        db = SessionLocal()
        try:
            candidates = db.query(ShadowAnswer).filter(
                ShadowAnswer.tenant_id == tenant_id,
                ShadowAnswer.workspace_id == workspace_id,
                ShadowAnswer.session_id == session_id
            ).all()

            if not candidates:
                return None

            query_embedding = np.asarray(self.semantic_cache.model.encode([query])[0])
            best_match = None
            max_sim = 0

            for c in candidates:
                c_emb = np.frombuffer(bytes(c.embedding), dtype='float32') # type: ignore
                sim = float(np.dot(query_embedding, c_emb))
                if sim > max_sim:
                    max_sim = sim
                    best_match = c

            if best_match is not None and max_sim > 0.90:
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
