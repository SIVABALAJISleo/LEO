"""
hyper/integrations/blender/HyperBlender/analyzer/scene_analyzer.py
"""
import time
from typing import Any, Dict, List
import numpy as np


class BlenderSceneAnalyzer:
    """Analyzes active Blender scene graph objects, modifiers, materials, and lights."""
    def __init__(self):
        self.previous_transforms: Dict[str, np.ndarray] = {}

    def analyze_scene_objects(self, scene_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        changed_count = 0
        total_poly_count = 0
        for obj in scene_data:
            name = obj.get("name", "")
            poly = obj.get("poly_count", 0)
            total_poly_count += poly
            mat = obj.get("matrix_world", np.eye(4))
            if name in self.previous_transforms:
                if np.max(np.abs(mat - self.previous_transforms[name])) > 1e-4:
                    changed_count += 1
            else:
                changed_count += 1
            self.previous_transforms[name] = mat

        return {
            "total_objects": len(scene_data),
            "changed_objects": changed_count,
            "total_poly_count": total_poly_count,
            "static_ratio": round((len(scene_data) - changed_count) / max(1, len(scene_data)), 3),
        }
