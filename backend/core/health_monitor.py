"""
backend/core/health_monitor.py
System Health Monitoring (Point 9).

Continuously tracks latency and CPU usage to trigger automatic adjustments.
"""
import asyncio
import logging
import psutil
from typing import List

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Continuous Health Monitoring: Latency & CPU (Point 9).
    """
    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.latency_history: List[float] = []
        self.cpu_history: List[float] = []
        self.running = False

    def log_latency(self, latency_ms: float):
        """Points 3, 9: Track request latency trends."""
        self.latency_history.append(latency_ms)
        if len(self.latency_history) > 50:
            self.latency_history.pop(0)

    async def run(self):
        """Main monitoring loop."""
        self.running = True
        from backend.core.chaos_controller import global_chaos_controller
        from backend.core.metrics import CPU_USAGE
        
        while self.running:
            try:
                # CPU Monitoring
                cpu = psutil.cpu_percent(interval=None)
                CPU_USAGE.set(cpu)
                
                # Latency Trend (Moving average of last 10)
                avg_latency = sum(self.latency_history[-10:]) / max(len(self.latency_history[-10:]), 1)
                
                # Point 4 & 9: Trigger adaptive mode switching
                global_chaos_controller.check_health(cpu, avg_latency)
                
                if cpu > 85.0:
                    logger.warning(f"health_monitor: HIGH CPU ({cpu}%). Triggering REDUCED mode.")
                    
            except Exception as e:
                logger.error(f"health_monitor: Error in check cycle - {e}")
                
            await asyncio.sleep(self.check_interval)

global_health_monitor = HealthMonitor()
