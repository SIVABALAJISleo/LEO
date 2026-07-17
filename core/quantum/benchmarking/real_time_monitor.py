"""
LEO Real-Time Performance Monitor
Exposes runtime compute indicators during model generation turns.
"""
import time
import psutil
from typing import Dict, Any

class RealTimeMonitor:
    """
    Poller to track system vitals under active inference execution.
    """
    
    def __init__(self):
        self.start_time = time.time()
        
    def sample(self) -> Dict[str, Any]:
        """Collects current memory and processor usage metrics"""
        mem = psutil.virtual_memory()
        cpu_load = psutil.cpu_percent()
        
        return {
            'uptime_sec': round(time.time() - self.start_time, 2),
            'cpu_utilization_pct': cpu_load,
            'ram_used_gb': round(mem.used / (1024**3), 2),
            'ram_available_gb': round(mem.available / (1024**3), 2)
        }
