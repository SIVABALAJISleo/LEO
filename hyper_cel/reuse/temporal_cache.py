"""
hyper_cel/reuse/temporal_cache.py
=============================================================================
HYPER-CEL: Temporal Reservoir & Intermediate Reuse Cache (Level 1 & Level 2)
=============================================================================
Provides state persistence across consecutive iterations, simulation time-steps,
and rendering frames for continuous sample reuse.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, Optional, List

class ComputationReservoir:
    """
    Generalized computation reservoir holding candidate samples, confidence weights, and age.
    """

    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.samples: Dict[str, Dict[str, Any]] = {}

    def store_sample(self, key: str, payload: Any, confidence: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        if len(self.samples) >= self.capacity:
            # Evict sample with lowest weight / highest age
            oldest_k = min(self.samples.keys(), key=lambda k: self.samples[k]["weight"] / (1.0 + time.time() - self.samples[k]["timestamp"]))
            del self.samples[oldest_k]

        self.samples[key] = {
            "payload": payload,
            "weight": confidence,
            "timestamp": time.time(),
            "reuse_count": 0,
            "metadata": metadata or {}
        }

    def fetch_sample(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.samples:
            s = self.samples[key]
            s["reuse_count"] += 1
            return s
        return None

class TemporalFrameBuffer:
    """
    Temporal history buffer for graphics / simulation reprojection.
    """

    def __init__(self, history_len: int = 4):
        self.history_len = history_len
        self.history: List[Dict[str, Any]] = []

    def push_frame(self, frame_tensor: np.ndarray, camera_or_state_transform: Optional[np.ndarray] = None):
        if len(self.history) >= self.history_len:
            self.history.pop(0)
        self.history.append({
            "tensor": np.copy(frame_tensor),
            "transform": camera_or_state_transform,
            "timestamp": time.time()
        })

    def get_previous_frame(self) -> Optional[np.ndarray]:
        if self.history:
            return self.history[-1]["tensor"]
        return None

    def project_previous_frame(self, current_transform: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        if not self.history:
            return None
        prev = self.history[-1]["tensor"]
        # If transforms are identical or None, direct temporal reuse
        return np.copy(prev)
