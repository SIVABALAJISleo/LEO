import time

class TemporalSimilarityScorer:
    """
    Decays novelty based on how recently similar things were seen.
    If we saw something similar very recently, it is NOT novel.
    If we saw it a long time ago, it might be considered slightly more novel due to context shift.
    """
    
    def __init__(self, decay_halflife_seconds: float = 3600.0):
        self.decay_halflife = decay_halflife_seconds
        
    def score(self, max_similarity: float, time_since_last_seen: float) -> float:
        """
        Calculates a temporal novelty modifier.
        Returns a multiplier in [0.0, 1.0].
        - 0.0 means completely redundant (saw exact thing recently).
        - 1.0 means completely novel (either not seen, or seen very long ago, or low similarity).
        """
        if max_similarity <= 0.0:
            return 1.0 # Not similar at all, so full novelty
            
        # Exponential decay of similarity over time
        # E.g., if halflife is 1 hour, then an identical query 1 hour ago is considered 50% similar now.
        temporal_sim = max_similarity * (0.5 ** (time_since_last_seen / self.decay_halflife))
        
        # Temporal novelty is the inverse of temporal similarity
        temporal_novelty = 1.0 - temporal_sim
        return max(0.0, min(1.0, temporal_novelty))
