import zlib
from ..schemas.contracts import ComplexityLevel

class HardnessDetector:
    """
    LAYER 1: HARDNESS + ENTROPY DETECTOR
    Calculates entropy (compression), complexity (token count), and novelty (mocked distance).
    """
    def __init__(self, simple_threshold=30, hard_threshold=200):
        self.simple_threshold = simple_threshold
        self.hard_threshold = hard_threshold

    def analyze(self, query: str) -> dict:
        # Entropy Score: zlib compression ratio
        compressed = zlib.compress(query.encode())
        entropy = len(compressed) / len(query) if len(query) > 0 else 0
        
        # Complexity: Word count
        word_count = len(query.split())
        
        # Novelty Score (Mock distance to cache centroids)
        novelty = 0.5 

        level = ComplexityLevel.MEDIUM
        if word_count < self.simple_threshold and entropy < 0.5:
            level = ComplexityLevel.SIMPLE
        elif word_count > self.hard_threshold or entropy > 0.8:
            level = ComplexityLevel.HARD
        
        # EXTREME Detection: Very high entropy + high length
        if word_count > 350 and entropy > 0.85:
            level = ComplexityLevel.EXTREME

        return {
            "level": level,
            "entropy": entropy,
            "novelty": novelty,
            "budget_ms": 100 if level == ComplexityLevel.SIMPLE else 600
        }

detector = HardnessDetector()

