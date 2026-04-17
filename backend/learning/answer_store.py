import logging
import numpy as np
import re
from typing import Optional, Dict, Any
from backend.core.database import SessionLocal, PrecomputedAnswer
from backend.intelligence.router import SemanticCache
from backend.graph.fragment_graph import global_fragment_graph
from backend.memory.global_memory import global_memory

logger = logging.getLogger(__name__)

class ContinuousLearningEngine:
    """
    Continuous Learning Loop.
    Decomposes every high-confidence answer into fragments for the Knowledge Graph.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()

    async def learn(self, query: str, answer: str, confidence: float, tenant_id: str = "default", workspace_id: str = "default"):
        """
        Evaluates and stores high-confidence results (Threshold 0.85).
        Decomposes into fragments.
        """
        if confidence < 0.85: # Lowered from 0.95 (Phase 30)
            logger.info(f"skip_learning: confidence {confidence} too low")
            return

        # 0. Normalize to get entity
        from backend.normalization.normalizer import global_normalizer
        norm = global_normalizer.normalize(query)
        entity = norm["entity"]

        # 1. Store in Global Memory
        global_memory.log(query, answer, "LEARNED", entity, confidence)

        # 2. Fragment Decomposition (Rule-based for speed)
        fragments = self._decompose_to_fragments(answer)
        for f_type, f_content in fragments.items():
            global_fragment_graph.register_fragment(entity, f_type, f_content)
            
        logger.info(f"continuous_learning_applied: entity={entity} fragments={list(fragments.keys())}")

        # 3. Persistent DB storage (Layer 1 bypass)
        db = SessionLocal()
        try:
            embedding = np.asarray(self.semantic_cache.model.encode([query])[0])
            new_ans = PrecomputedAnswer(
                canonical_question=query,
                answer=answer,
                embedding=embedding.tobytes(),
                confidence=confidence,
                cluster_id=0,
                tenant_id=tenant_id,
                workspace_id=workspace_id
            )
            db.add(new_ans)
            db.commit()
        except Exception as e:
            logger.error(f"learning_db_failed: {e}")
            db.rollback()
        finally:
            db.close()

    def _decompose_to_fragments(self, answer: str) -> Dict[str, str]:
        """Heuristic-based decomposition of answer text into fragments."""
        fragments = {}
        
        # Simple regex split for common structures
        def_match = re.search(r"^(.*?)(?:\n\n|\nSteps:|\nExample:)", answer, re.S)
        if def_match: fragments["definition"] = def_match.group(1).strip()
        
        steps_match = re.search(r"Steps:\n(.*?)(?:\n\n|\nExample:|\nAdvantages:)", answer, re.S)
        if steps_match: fragments["steps"] = steps_match.group(1).strip()
        
        ex_match = re.search(r"Example:\n(.*?)(?:\n\n|\nAdvantages:|\nImportant:)", answer, re.S)
        if ex_match: fragments["examples"] = ex_match.group(1).strip()
        
        adv_match = re.search(r"Advantages:\n(.*?)(?:\n\n|\nImportant:)", answer, re.S)
        if adv_match: fragments["advantages"] = adv_match.group(1).strip()
        
        if not fragments: # If unstructured, treat as definition
            fragments["definition"] = answer
            
        return fragments

global_learning_engine = ContinuousLearningEngine()
