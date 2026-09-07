"""
cbe/importance/semantic_importance.py
Assigns semantic priority weights based on object category and task relevance.
Protects critical regions like UI, characters, and focus targets from aggressive downsampling.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional


class SemanticImportance:
    """
    Translates semantic segmentation or object tags into an importance weight map.
    """
    DEFAULT_WEIGHTS = {
        "ui": 1.00,
        "hud": 1.00,
        "character": 0.95,
        "player": 0.95,
        "vehicle": 0.85,
        "foliage": 0.60,
        "environment": 0.50,
        "terrain": 0.45,
        "sky": 0.25,
        "background": 0.25,
    }

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        self.weights = dict(self.DEFAULT_WEIGHTS)
        if custom_weights:
            self.weights.update(custom_weights)

    def compute(self, semantic_map: Optional[np.ndarray], height: int, width: int) -> np.ndarray:
        """
        semantic_map: (H, W) string or integer labels. If None, returns uniform baseline.
        """
        if semantic_map is None:
            return np.ones((height, width), dtype=np.float32) * 0.70
            
        output = np.zeros((height, width), dtype=np.float32)
        # Vectorized lookup for string or integer semantic classes
        unique_classes = np.unique(semantic_map)
        for c in unique_classes:
            key = str(c).lower().strip()
            w = self.weights.get(key, 0.50)
            output[semantic_map == c] = w
            
        return output
