"""
backend/core/chaos_controller.py
Chaos Controller (Point 1, 7).

Manages system processing modes: NORMAL, REDUCED, MINIMAL.
Detects stress signals and triggers graceful degradation.
"""
import logging
import enum
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChaosMode(enum.Enum):
    NORMAL = 1    # Full dominance pipeline
    REDUCED = 2   # Simple approximation, skip decomposition
    MINIMAL = 3   # Cache only, instant "Busy" templates

class ChaosController:
    """
    Unbreakable System Stability: Chaos Control Layer.
    Points 1, 7: Adaptive mode switching.
    """
    def __init__(self):
        self.mode = ChaosMode.NORMAL
        self.miss_count = 0
        self.last_switch = 0
        self.cpu_usage = 0.0

    def check_health(self, cpu_usage: float, recent_latency: float):
        """Points 3, 4, 9: Trigger automatic mode adjustments."""
        self.cpu_usage = cpu_usage
        
        # Transition Logic
        if cpu_usage > 90.0 or recent_latency > 45.0:
            self._switch_mode(ChaosMode.MINIMAL)
        elif cpu_usage > 75.0 or recent_latency > 35.0:
            self._switch_mode(ChaosMode.REDUCED)
        else:
            self._switch_mode(ChaosMode.NORMAL)

    def record_miss(self):
        """Detect Point 1: unknown query floods."""
        self.miss_count += 1
        if self.miss_count > 100: # Simple spike detection
            logger.warning("chaos_controller: FLOOD DETECTED. Switching to REDUCED.")
            self._switch_mode(ChaosMode.REDUCED)
            self.miss_count = 0

    def _switch_mode(self, new_mode: ChaosMode):
        if self.mode != new_mode:
            logger.info(f"chaos_controller: MODE SWITCH {self.mode.name} -> {new_mode.name}")
            self.mode = new_mode

    def get_mode(self) -> ChaosMode:
        return self.mode

global_chaos_controller = ChaosController()
