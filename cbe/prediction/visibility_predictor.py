"""
cbe/prediction/visibility_predictor.py
Predicts frustum entry/exit and occlusion status for scene bounding volumes.
Pre-culls invisible geometry before draw call or ray dispatch.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Tuple


class VisibilityPredictor:
    """
    Frustum and occlusion predictor evaluating whether objects are visible
    in predicted camera view-projection space.
    """
    def is_box_visible(
        self,
        box_min: np.ndarray,
        box_max: np.ndarray,
        view_proj_matrix: np.ndarray
    ) -> bool:
        """
        Tests whether an AABB [box_min, box_max] intersects the camera frustum.
        Transforms 8 box vertices into clip space.
        """
        corners = np.array([
            [box_min[0], box_min[1], box_min[2], 1.0],
            [box_max[0], box_min[1], box_min[2], 1.0],
            [box_min[0], box_max[1], box_min[2], 1.0],
            [box_max[0], box_max[1], box_min[2], 1.0],
            [box_min[0], box_min[1], box_max[2], 1.0],
            [box_max[0], box_min[1], box_max[2], 1.0],
            [box_min[0], box_max[1], box_max[2], 1.0],
            [box_max[0], box_max[1], box_max[2], 1.0],
        ], dtype=np.float32)
        
        # Transform to clip space
        clip_corners = np.matmul(corners, view_proj_matrix.T)
        w = clip_corners[:, 3]
        
        # Behind camera plane check
        if np.all(w <= 0.0):
            return False
            
        # Frustum planes: -w <= x,y,z <= w
        x = clip_corners[:, 0]
        y = clip_corners[:, 1]
        z = clip_corners[:, 2]
        
        # If all points are outside any single frustum plane, box is culled
        if np.all(x > w) or np.all(x < -w):
            return False
        if np.all(y > w) or np.all(y < -w):
            return False
        if np.all(z > w) or np.all(z < 0.0):
            return False
            
        return True
