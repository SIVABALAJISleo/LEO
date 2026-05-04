import time
from typing import Dict, Any, List

class MonitoringService:
    """
    23. ERROR HARVEST SYSTEM
    26. DRIFT MONITORING
    """
    def __init__(self):
        self.error_logs: List[Dict[str, Any]] = []
        self.request_history: List[float] = []

    def log_error(self, error_type: str, details: str):
        self.error_logs.append({
            "timestamp": time.time(),
            "type": error_type,
            "details": details
        })

    def detect_drift(self) -> bool:
        # Simple frequency-based drift detection mock
        now = time.time()
        recent = [t for t in self.request_history if now - t < 3600]
        self.request_history.append(now)
        
        # If sudden spike in requests, signal potential drift/anomaly
        return len(recent) > 1000 

