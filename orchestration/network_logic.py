import logging
import time
from collections import deque
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class NetworkHitLogic:
    """
    Implements a server-side rewind history buffer for event validation.
    Compensates for CPU orchestration latency by allowing "rewind" lookups.
    """
    def __init__(self, buffer_size_sec: float = 1.0, tick_rate: int = 60):
        self.buffer_size = int(buffer_size_sec * tick_rate)
        self.history = deque(maxlen=self.buffer_size)
        logger.info(f"NetworkHitLogic initialized with {self.buffer_size} frame buffer")

    def record_state(self, state: Dict[str, Any]):
        """
        Save the world state at the current timestamp.
        """
        self.history.append({
            "timestamp": time.time(),
            "state": state
        })

    def validate_event(self, event_timestamp: float, event_data: Dict[str, Any]) -> bool:
        """
        Look back in time to validate if an event (e.g., a hit) was valid.
        """
        logger.info(f"Validating event at {event_timestamp}")
        
        # Find the state closest to the event timestamp
        closest_state = None
        min_diff = float('inf')
        
        for record in self.history:
            diff = abs(record["timestamp"] - event_timestamp)
            if diff < min_diff:
                min_diff = diff
                closest_state = record
                
        if closest_state:
            # Simple interpolation logic could go here if we had two states
            # For now, just check the time delta
            if min_diff < 0.05: # 50ms tolerance
                logger.info(f"Found matching state with diff {min_diff:.4f}s")
                return True
            elif min_diff < 0.1: # 100ms tolerance with warning
                logger.warning(f"Found loose matching state with diff {min_diff:.4f}s")
                return True
                
        logger.warning(f"Event validation failed: No state found within tolerance (closest: {min_diff:.4f}s)")
        return False
            
        logger.warning("Event validation failed: No matching history found")
        return False
