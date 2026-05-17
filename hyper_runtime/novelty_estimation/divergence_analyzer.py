import numpy as np

class EmbeddingDivergenceAnalyzer:
    """
    Analyzes how much a new embedding diverges from known context/history.
    High divergence means high novelty.
    """
    
    def __init__(self):
        pass
        
    def _normalize(self, v: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def calculate_divergence(self, input_embedding: np.ndarray, context_embeddings: list[np.ndarray]) -> float:
        """
        Calculates cosine distance (1 - cosine similarity) to the nearest context.
        Returns a value in [0, 1]. 1.0 means completely orthogonal/opposite (highly novel).
        0.0 means identical (zero novelty).
        """
        if not context_embeddings:
            return 1.0 # Completely novel if no context exists
            
        emb_norm = self._normalize(input_embedding)
        
        max_sim = -1.0
        for ctx_emb in context_embeddings:
            ctx_norm = self._normalize(ctx_emb)
            sim = np.dot(emb_norm, ctx_norm)
            if sim > max_sim:
                max_sim = sim
                
        # Divergence is 1 - max similarity (clamped between 0 and 1)
        divergence = 1.0 - np.clip(max_sim, 0.0, 1.0)
        return divergence
