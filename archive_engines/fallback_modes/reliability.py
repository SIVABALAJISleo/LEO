import psutil
import logging
from enum import Enum
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemMode(Enum):
    FAST = "fast"           # Max approximation, lowest compute
    BALANCED = "balanced"   # Perceptual equivalence
    ACCURATE = "accurate"   # High fidelity refinement

class ReliabilityManager:
    """
    Monitors system health and enforces performance modes.
    Ensures graceful degradation under heavy load.
    """
    def __init__(self, high_load_threshold: float = 85.0):
        self.high_load_threshold = high_load_threshold
        self.override_mode: Optional[SystemMode] = None

    def get_current_mode(self, requested: str = "balanced") -> SystemMode:
        # Check for hardware saturation
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        
        load = max(cpu, mem)
        
        if load > self.high_load_threshold:
            logger.warning(f"SYSTEM SATURATION DETECTED ({load}%). Forcing FAST mode.")
            return SystemMode.FAST
            
        try:
            return SystemMode(requested.lower())
        except ValueError:
            return SystemMode.BALANCED

    def get_config_for_mode(self, mode: SystemMode) -> Dict[str, Any]:
        configs = {
            SystemMode.FAST: {
                "upscale": False,
                "refinement": False,
                "probabilistic": True,
                "cache_only": True
            },
            SystemMode.BALANCED: {
                "upscale": "perceptual",
                "refinement": "async",
                "probabilistic": True,
                "cache_only": False
            },
            SystemMode.ACCURATE: {
                "upscale": "high_res",
                "refinement": "sync",
                "probabilistic": False,
                "cache_only": False
            }
        }
        return configs.get(mode)
