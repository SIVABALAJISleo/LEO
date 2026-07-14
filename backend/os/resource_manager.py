import psutil
import time
import logging
import threading
from typing import Dict, Any

logger = logging.getLogger(__name__)

class IntelligentResourceManager:
    """
    Subsystem 17: Intelligent Resource Manager.
    Monitors CPU, Threads, RAM, SSD, and conceptually iGPU.
    Adapts execution dynamically to hardware limitations.
    """
    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.stats: Dict[str, Any] = {
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "available_ram_gb": 0.0,
            "disk_percent": 0.0,
            "thread_count": 0,
            "is_throttled": False
        }
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Intelligent Resource Manager started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            
    def _monitor_loop(self):
        while self.running:
            try:
                self.stats["cpu_percent"] = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                self.stats["ram_percent"] = mem.percent
                self.stats["available_ram_gb"] = mem.available / (1024 ** 3)
                
                disk = psutil.disk_usage('/')
                self.stats["disk_percent"] = disk.percent
                
                # Psutil doesn't natively do iGPU telemetry without Windows WMI or Linux sysfs hacks.
                # We will simulate iGPU load telemetry based on active OpenVINO/SYCL requests mapped later.
                
                # Adaptive Throttling Logic
                # If RAM > 90% or CPU > 95%, we enter throttled state
                if self.stats["ram_percent"] > 90.0 or self.stats["cpu_percent"] > 95.0:
                    if not self.stats["is_throttled"]:
                        logger.warning(f"Resource Manager entering THROTTLED state. CPU: {self.stats['cpu_percent']}%, RAM: {self.stats['ram_percent']}%")
                    self.stats["is_throttled"] = True
                else:
                    if self.stats["is_throttled"]:
                        logger.info("Resource Manager recovering from throttled state.")
                    self.stats["is_throttled"] = False
                    
            except Exception as e:
                logger.error(f"Resource Manager error: {e}")
                
            time.sleep(self.check_interval)

    def get_current_stats(self) -> Dict[str, Any]:
        return dict(self.stats)

    def can_accept_heavy_task(self) -> bool:
        """Returns True if the system has enough headroom for an LLM inference task."""
        return not self.stats["is_throttled"] and self.stats["available_ram_gb"] > 2.0
