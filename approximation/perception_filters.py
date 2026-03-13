import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PerceptionOptimizer:
    """
    Minimizes vision compute via ROI focus and temporal differencing.
    """
    def __init__(self, threshold: float = 30.0):
        self.threshold = threshold
        self.last_frame: Optional[np.ndarray] = None

    def get_regions_of_interest(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects areas of motion/change using simple frame differencing.
        """
        if self.last_frame is None:
            self.last_frame = frame
            return [(0, 0, frame.shape[1], frame.shape[0])] # Full frame initially
            
        diff = np.abs(frame.astype(float) - self.last_frame.astype(float))
        change_mask = np.mean(diff, axis=-1) > self.threshold
        
        # Simple bounding box for the entire changed area (or sub-tiles)
        coords = np.argwhere(change_mask)
        if coords.size == 0:
            return []
            
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        
        self.last_frame = frame
        logger.info(f"ROI Detected: ({x0}, {y0}) to ({x1}, {y1})")
        return [(x0, y0, x1, y1)]

    def apply_batch_approximation(self, data: List[float]) -> float:
        """Probabilistic aggregation for large numerical datasets."""
        # Equivalent to HyperLogLog or Reservoir Sampling integration
        return np.mean(data) # Simplified for demo
