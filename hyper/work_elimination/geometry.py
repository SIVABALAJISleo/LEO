"""
hyper/work_elimination/geometry.py
==================================
HYPER Geometry Work Elimination:
Dynamic Level of Detail (LOD), mesh simplification selection, proxy geometry,
and instanced mesh reuse.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class GeometryEliminationEngine:
    """
    Eliminates redundant geometric detail by:
    - Automatically computing optimal discrete LOD levels based on screen pixel size.
    - Swapping complex meshes for low-poly collision or proxy geometry when distant.
    - Grouping identical meshes into hardware instancing batches.
    """

    def __init__(self, lod_screen_thresholds: Optional[List[float]] = None):
        # Screen coverage fraction thresholds: [LOD0 (>0.3), LOD1 (>0.1), LOD2 (>0.03), LOD3 (>0.005)]
        self.lod_thresholds = lod_screen_thresholds or [0.25, 0.08, 0.02, 0.005]
        self.mesh_cache: Dict[str, Any] = {}

    def select_lod_level(
        self,
        bounding_radius_world: float,
        distance_to_camera: float,
        fov_degrees: float = 90.0,
        screen_height_pixels: int = 1080,
    ) -> int:
        """
        Determines the LOD index (0 = highest detail, 3 = lowest detail, 4 = culled/proxy).
        """
        if distance_to_camera <= 0.1:
            return 0

        # Projected screen height fraction: (2 * r / dist) / (2 * tan(fov/2))
        fov_rad = np.radians(fov_degrees)
        tan_half_fov = np.tan(fov_rad * 0.5)
        screen_fraction = (bounding_radius_world / distance_to_camera) / tan_half_fov

        for lod_idx, thresh in enumerate(self.lod_thresholds):
            if screen_fraction >= thresh:
                return lod_idx

        return len(self.lod_thresholds)  # Proxy or extreme simplification

    def batch_instances(
        self, objects: List[Dict[str, Any]]
    ) -> Dict[str, List[np.ndarray]]:
        """
        Groups identical meshes into instanced transform arrays:
        Returns: {mesh_hash: [4x4_transform_matrices]}
        """
        batches: Dict[str, List[np.ndarray]] = {}
        for obj in objects:
            mhash = obj.get("mesh_hash", "default")
            trans = np.array(obj.get("transform", np.eye(4)), dtype=np.float32)
            if mhash not in batches:
                batches[mhash] = []
            batches[mhash].append(trans)
        return batches
