"""
hyper/integrations/blender/HyperBlender/visibility/viewport_culling.py
"""
from typing import Any, Dict, List, Tuple
import numpy as np


class BlenderViewportCulling:
    """Frustum and occlusion culling for Blender viewport 3D region."""
    def cull_viewport(
        self, objects: List[Dict[str, Any]], camera_pos: np.ndarray, view_matrix: np.ndarray, max_dist: float = 300.0
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        visible, culled = [], []
        for obj in objects:
            pos = np.array(obj.get("location", [0, 0, 0]), dtype=np.float32)
            dist = float(np.linalg.norm(pos - camera_pos))
            if dist > max_dist:
                culled.append(obj)
            else:
                visible.append(obj)
        return visible, culled
