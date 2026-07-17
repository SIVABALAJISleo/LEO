"""
Performance Monitor for LEO Quantum heterogeneous engine.
Tracks throughput, latencies, and device status in real-time.
"""
import time
from typing import Dict, Any

class PerformanceMonitor:
    """
    Performance profiling tool to track engine scheduling metrics.
    """
    
    def __init__(self):
        self.metrics_history = []
        self.total_runs = 0
        
    def update_metrics(self, strategy: str, system_state: Dict[str, Any]):
        """Record a single execution run's metadata"""
        self.total_runs += 1
        record = {
            'timestamp': time.time(),
            'strategy': strategy,
            'cpu_utilization': system_state.get('cpu_utilization', 0.0),
            'temperature': system_state.get('temperature', 45.0),
            'thermal_state': system_state.get('thermal_state', 'normal')
        }
        self.metrics_history.append(record)
        # Keep only the last 1000 records
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for scheduler profiling"""
        if not self.metrics_history:
            return {'runs': 0, 'avg_cpu': 0.0}
            
        avg_cpu = sum(x['cpu_utilization'] for x in self.metrics_history) / len(self.metrics_history)
        return {
            'runs': self.total_runs,
            'avg_cpu': round(avg_cpu, 2),
            'last_strategy': self.metrics_history[-1]['strategy']
        }
