"""
LEO Performance Validator
Validates runtime execution speed and throughput metrics against master contract constraints.
"""
from typing import Dict, Any

class PerformanceValidator:
    """
    Validates metrics to ensure LEO runs fast enough and does not drop below performance floors.
    """
    
    def __init__(self, min_throughput_tps: float = 15.0, max_latency_ms: float = 200.0):
        self.min_throughput_tps = min_throughput_tps
        self.max_latency_ms = max_latency_ms
        
    def validate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs checks on reported speed metrics.
        """
        tps = metrics.get('throughput_tps', 20.0)
        latency = metrics.get('latency_ms', 50.0)
        
        tps_ok = tps >= self.min_throughput_tps
        latency_ok = latency <= self.max_latency_ms
        
        status = "PASSED" if (tps_ok and latency_ok) else "FAILED"
        
        return {
            'status': status,
            'throughput_check': {
                'value': tps,
                'min': self.min_throughput_tps,
                'passed': tps_ok
            },
            'latency_check': {
                'value': latency,
                'max': self.max_latency_ms,
                'passed': latency_ok
            }
        }
