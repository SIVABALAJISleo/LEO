"""
backend/core/chaos_controller.py
Chaos Controller (Point 1, 7).

Manages system processing modes: NORMAL, REDUCED, MINIMAL.
Detects stress signals and triggers graceful degradation.
"""
import logging
import enum
import time
import psutil
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
        self.last_switch = time.time()
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.latency_samples = []

    def check_health(self, cpu_usage: float, recent_latency: float):
        """Points 3, 4, 9: Trigger automatic mode adjustments."""
        self.cpu_usage = cpu_usage
        self.memory_usage = psutil.virtual_memory().percent
        
        # Keep track of latency tail
        self.latency_samples.append(recent_latency)
        if len(self.latency_samples) > 10:
            self.latency_samples.pop(0)
        
        avg_latency = sum(self.latency_samples) / len(self.latency_samples)

        # Transition Logic
        # Point 4: Memory pressure guard
        if cpu_usage > 90.0 or self.memory_usage > 90.0 or avg_latency > 48.0:
            self._switch_mode(ChaosMode.MINIMAL)
        elif cpu_usage > 75.0 or self.memory_usage > 80.0 or avg_latency > 35.0:
            self._switch_mode(ChaosMode.REDUCED)
        else:
            # Only go back to normal if pulse is truly stable
            if cpu_usage < 50.0 and self.memory_usage < 70.0 and avg_latency < 20.0:
                self._switch_mode(ChaosMode.NORMAL)

    def record_miss(self):
        """Detect Point 1: unknown query floods and chaotic spikes."""
        self.miss_count += 1
        if self.miss_count > 50: # More aggressive flood detection
            logger.warning("chaos_controller: FLOOD/CHAOS DETECTED. Switching to REDUCED.")
            self._switch_mode(ChaosMode.REDUCED)
            self.miss_count = 0

    def _switch_mode(self, new_mode: ChaosMode):
        if self.mode != new_mode:
            logger.warning(f"chaos_controller: SYSTEM MODE SHIFT {self.mode.name} -> {new_mode.name} (CPU: {self.cpu_usage}%, MEM: {self.memory_usage}%)")
            self.mode = new_mode
            self.last_switch = time.time()

    def get_mode(self) -> ChaosMode:
        return self.mode

global_chaos_controller = ChaosController()
