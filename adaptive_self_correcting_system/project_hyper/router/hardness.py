import zlib
from ..schemas.contracts import ComplexityLevel

class HardnessDetector:
    """
    LAYER 1: HARDNESS DETECTOR
    Classifies input into SIMPLE, MEDIUM, or HARD based on entropy and length.
    """
    def __init__(self, simple_threshold=25, hard_threshold=200):
        self.simple_threshold = simple_threshold
        self.hard_threshold = hard_threshold

    def analyze(self, query: str) -> dict:
        word_count = len(query.split())
        
        # Entropy Proxy: zlib compression ratio
        compressed = zlib.compress(query.encode())
        entropy_ratio = len(compressed) / len(query) if len(query) > 0 else 0
        
        # Novelty Proxy (Mocked until cache is ready)
        novelty_score = 0.5 

        level = ComplexityLevel.MEDIUM
        if word_count < self.simple_threshold and entropy_ratio < 0.6:
            level = ComplexityLevel.SIMPLE
        elif word_count > self.hard_threshold or entropy_ratio > 0.8:
            level = ComplexityLevel.HARD
            
        return {
            "level": level,
            "entropy": entropy_ratio,
            "novelty": novelty_score,
            "budget_ms": 100 if level == ComplexityLevel.SIMPLE else 500
        }

hardness_detector = HardnessDetector()

