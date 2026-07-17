"""
Recursive Self-Crystallizer
Feedback loop that monitors model execution, learns repeat query patterns,
and pre-crystallizes their hypervectors dynamically to bypass neural pipelines.
"""
import logging
from collections import Counter
from typing import Dict, Any, Optional
from core.quantum.breakthrough.vsa_crystallizer_v2 import VSACrystallizerV2

logger = logging.getLogger(__name__)

class RecursiveCrystallizer:
    """
    Learns query recurrences and pre-materializes VSA keys.
    System execution speed accelerates as query history increases.
    """
    
    def __init__(self, vsa_engine: VSACrystallizerV2, auto_crystallize_threshold: int = 3):
        self.vsa = vsa_engine
        self.threshold = auto_crystallize_threshold
        self.query_frequency = Counter()
        self.crystallized_queries = set()
        
    def record_and_evaluate(self, query: str, final_response: str) -> bool:
        """
        Logs a query transaction.
        If it exceeds the frequency threshold, pre-materializes its VSA representation.
        """
        cleaned = " ".join(query.lower().strip().split())
        self.query_frequency[cleaned] += 1
        
        # Check if we should crystallize
        if self.query_frequency[cleaned] >= self.threshold and cleaned not in self.crystallized_queries:
            try:
                self.vsa.crystallize_query(query, final_response)
                self.crystallized_queries.add(cleaned)
                logger.info(f"[RecursiveCrystallization] crystallized query schema: '{query[:30]}...' -> VSA space.")
                return True
            except Exception as e:
                logger.debug(f"Failed to crystallize query: {e}")
                
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics for reinforcement learning evaluation"""
        return {
            'total_crystallized': len(self.crystallized_queries),
            'top_query_frequencies': dict(self.query_frequency.most_common(5))
        }
