import zlib
from .contracts import RiskLevel

class LimitDetector:
    """
    MODULE 1: LIMIT DETECTOR
    Detects low confidence, high entropy, novel input, or timeout risk.
    """
    def detect(self, prompt: str) -> dict:
        word_count = len(prompt.split())
        
        # Entropy check (compressibility)
        compressed = zlib.compress(prompt.encode())
        entropy_ratio = len(compressed) / len(prompt) if len(prompt) > 0 else 0
        
        # Risk heuristics
        risk = RiskLevel.LOW
        confidence = 0.95
        
        if entropy_ratio > 0.8:
            risk = RiskLevel.MEDIUM
            confidence = 0.7
            
        if word_count > 200:
            risk = RiskLevel.HIGH
            confidence = 0.4
            
        if "???" in prompt or len(prompt) < 5:
            risk = RiskLevel.CRITICAL
            confidence = 0.2

        return {
            "risk_level": risk,
            "confidence_estimate": confidence
        }

limit_detector = LimitDetector()
吐
