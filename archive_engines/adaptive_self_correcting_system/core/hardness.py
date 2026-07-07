import zlib
from enum import Enum

class QueryHardness(str, Enum):
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class HardnessDetector:
    """
    Analyzes input BEFORE computation to classify execution path.
    Replaces brute-force logic with informational audit.
    """
    def __init__(self, simple_threshold=20, hard_threshold=250):
        self.simple_threshold = simple_threshold
        self.hard_threshold = hard_threshold

    def audit(self, query: str) -> QueryHardness:
        # 1. Structural Audit (Length)
        word_count = len(query.split())
        
        # 2. Informational Audit (Compressibility)
        # Ratio of compressed vs original size.
        # High ratio (0.8+) = high entropy (Complex/Unique)
        # Low ratio (0.1-0.4) = low entropy (Structured/Simple)
        compressed = zlib.compress(query.encode())
        entropy_ratio = len(compressed) / len(query) if len(query) > 0 else 0
        
        if word_count < self.simple_threshold and entropy_ratio < 0.5:
            return QueryHardness.SIMPLE
        
        if word_count > self.hard_threshold or entropy_ratio > 0.8:
            return QueryHardness.HARD
            
        return QueryHardness.MEDIUM

# Singleton instance
detector = HardnessDetector()

