from typing import List
from ..models.schemas import DriftMetrics

class DriftController:
    """
    12) DRIFT CONTROL
    - monitor output distribution (EWMA)
    - detect anomalies
    - rollback behavioral state if degraded
    """
    def __init__(self, alpha: float = 0.1, threshold: float = 3.0):
        self.alpha = alpha
        self.threshold = threshold
        self.ewma = 0.0
        self.history: List[float] = []

    def update(self, confidence_score: float) -> DriftMetrics:
        # Simple EWMA update
        self.ewma = (self.alpha * confidence_score) + ((1 - self.alpha) * self.ewma)
        self.history.append(confidence_score)
        
        # Simple CUSUM simulation
        cusum = sum(self.history[-10:]) / 10 if len(self.history) >= 10 else 0.0
        
        anomaly = abs(confidence_score - self.ewma) > self.threshold
        
        return DriftMetrics(
            ewma=self.ewma,
            cusum=cusum,
            anomaly_detected=anomaly
        )

