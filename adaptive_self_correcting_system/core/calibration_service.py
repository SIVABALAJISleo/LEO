import math
from typing import List

class CalibrationService:
    """
    10. CONFIDENCE CALIBRATION
    - Temperature scaling
    - Normalization
    """
    def __init__(self, temperature: float = 1.5):
        self.temperature = temperature

    def calibrate(self, confidences: List[float]) -> float:
        if not confidences: return 0.0
        
        # Apply temperature scaling (simplified)
        scaled = [math.pow(c, 1/self.temperature) for c in confidences]
        
        # Return average of scaled confidences
        return sum(scaled) / len(scaled)
吐
