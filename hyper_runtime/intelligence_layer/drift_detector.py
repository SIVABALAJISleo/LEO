import numpy as np
import logging

logger = logging.getLogger("HyperCore.DriftDetector")

class ADWINDriveDetector:
    """
    HyperCore INTELLIGENCE LAYER — Drift Detection & Shadow Exploration
    
    A lightweight implementation of the Adaptive Windowing (ADWIN) algorithm.
    It monitors the stream of routing rewards to detect distribution shifts
    (e.g., if a previously reliable shortcut starts failing because of drift).
    """
    def __init__(self, delta: float = 0.05):
        self.delta = delta
        self.window = []
        
    def add_element(self, value: float) -> bool:
        """
        Adds a new metric to the sliding window.
        Returns True if a statistical drift is detected.
        """
        self.window.append(value)
        
        # Check for split-window variances if window is large enough
        n = len(self.window)
        if n < 20:
            return False
            
        # Try to find a split point where the means of the two sub-windows differ significantly
        for i in range(10, n - 10):
            w1 = self.window[:i]
            w2 = self.window[i:]
            
            m1 = np.mean(w1)
            m2 = np.mean(w2)
            
            # Simple threshold for deviation (T-test style heuristic for simulation)
            epsilon = np.sqrt((1.0 / (2 * len(w1)) + 1.0 / (2 * len(w2))) * np.log(2.0 / self.delta))
            
            if abs(m1 - m2) > epsilon:
                logger.warning(f"ADWIN Drift Detected! Mean shifted from {m1:.4f} to {m2:.4f}. Resetting window.")
                # Shrink window to contain only the newer distribution
                self.window = w2
                return True
                
        return False
