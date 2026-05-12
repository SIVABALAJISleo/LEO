import numpy as np

class AdaptiveComputeRouter:
    """
    Implements adaptive compute routing (Section 20).
    Never use expensive compute when cheap compute is sufficient.
    """
    def __init__(self):
        self.complexity_thresholds = {
            "retrieval": 0.2,
            "tiny_student": 0.5,
            "sparse_moe": 0.8
        }
        
    def estimate_complexity(self, query_embedding):
        """
        Lightweight neural estimator to predict required compute path.
        Returns a float between 0.0 (trivial) and 1.0 (highly complex).
        """
        return np.clip(np.mean(np.abs(query_embedding)) * 10.0, 0.0, 1.0)
        
    def route_query(self, query_embedding):
        complexity = self.estimate_complexity(query_embedding)
        
        if complexity < self.complexity_thresholds["retrieval"]:
            return "PATH_RETRIEVAL_ONLY"
        elif complexity < self.complexity_thresholds["tiny_student"]:
            return "PATH_TINY_STUDENT"
        elif complexity < self.complexity_thresholds["sparse_moe"]:
            return "PATH_SPARSE_MOE"
        else:
            return "PATH_DENSE_TEACHER"
