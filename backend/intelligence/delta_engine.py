import logging
import numpy as np
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class SemanticDeltaEngine:
    """
    Generates only the 'missing' parts of an answer by detecting overlap
    with existing cached results using embeddings.
    """
    
    def calculate_delta(self, query_emb: np.ndarray, candidate_emb: np.ndarray, candidate_answer: str) -> Optional[Dict[str, Any]]:
        """
        Detects how much of the query is 'new' compared to the candidate.
        If similarity is very high (>0.95), returns the candidate.
        If similarity is moderate (0.8 - 0.95), identifies the 'delta' needed.
        """
        similarity = float(np.dot(query_emb.flatten(), candidate_emb.flatten()) / 
                          (np.linalg.norm(query_emb) * np.linalg.norm(candidate_emb)))
        
        if similarity > 0.96:
            return {"mode": "FULL_MATCH", "base_answer": candidate_answer, "delta_required": False}
        
        if similarity > 0.85:
            # We have a strong base, but need a specific refinement
            return {
                "mode": "PARTIAL_MATCH",
                "base_answer": candidate_answer,
                "similarity": similarity,
                "delta_required": True,
                "reason": "semantic_overlap_detected"
            }
            
        return None

global_delta_engine = SemanticDeltaEngine()
