"""
LEO Predictive Prefetcher
Prefetches responses for anticipated subsequent user inputs based on transition probability matrices.
"""
from collections import defaultdict, deque
from typing import Optional


class PredictivePrefetcher:
    """
    Anticipates future queries based on sequence logs and prepares cached content.
    """
    
    def __init__(self, history_len: int = 100):
        self.history = deque(maxlen=history_len)
        # Transition counts: query_A -> next_query -> count
        self.transitions = defaultdict(lambda: defaultdict(int))
        
    def record_query(self, query: str):
        """Record query log for transition probability updates"""
        cleaned = self._clean_query(query)
        if self.history:
            prev = self.history[-1]
            self.transitions[prev][cleaned] += 1
            
        self.history.append(cleaned)
        
    def predict_next(self, current_query: str) -> Optional[str]:
        """Predicts the most probable next query based on prior transitions"""
        cleaned = self._clean_query(current_query)
        candidates = self.transitions[cleaned]
        if not candidates:
            return None
            
        # Return candidate with maximum count
        best_candidate = max(candidates.keys(), key=lambda k: candidates[k])
        return best_candidate

    def _clean_query(self, query: str) -> str:
        return " ".join(query.lower().strip().split())
