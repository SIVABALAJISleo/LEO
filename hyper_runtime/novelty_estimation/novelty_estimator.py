import numpy as np

class NoveltyEstimationEngine:
    """
    Module 3 — Novelty Estimation Engine
    Estimates how much new information exists in an input.
    Behavior:
    low novelty -> replay/retrieval
    medium novelty -> sparse execution
    high novelty -> dense execution
    """
    def __init__(self):
        self.entropy_history = []

    def estimate_novelty(self, input_embedding, context_embeddings):
        """
        Returns a novelty score in [0, 1].
        """
        if not context_embeddings:
            return 1.0 # Completely novel
            
        similarities = [np.dot(input_embedding, ctx) / 
                       (np.linalg.norm(input_embedding) * np.linalg.norm(ctx) + 1e-9) 
                       for ctx in context_embeddings]
        max_sim = np.max(similarities)
        
        novelty_score = 1.0 - np.clip(max_sim, 0.0, 1.0)
        
        self.entropy_history.append(novelty_score)
        if len(self.entropy_history) > 100:
            self.entropy_history.pop(0)
            
        return novelty_score
