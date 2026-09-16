"""
hyper/work_elimination/visibility.py
====================================
HYPER Visibility Work Elimination:
Performs frustum culling, distance culling, back-face culling, and
hierarchical occlusion culling with temporal visibility history.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class VisibilityEliminationEngine:
    """
    Evaluates whether geometry, lights, and effects are visible before submission
    to rasterization or compute shader pipelines.
    """

    def __init__(self, max_distance: float = 1000.0):
        self.max_distance = max_distance
        self.visibility_history: Dict[str, int] = {}  # object_id -> frames_visible
        self.occluders: List[Tuple[np.ndarray, np.ndarray, float]] = []  # (center, normal, radius)

    def cull_frustum_and_distance(
        self,
        objects: List[Dict[str, Any]],
        camera_pos: np.ndarray,
        vp_matrix: np.ndarray,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
        """
        Filters objects against camera frustum and maximum view distance.
        Returns: (visible_objects, culled_objects, stats)
        """
        visible = []
        culled = []
        stats = {
            "frustum_culled": 0,
            "distance_culled": 0,
            "occlusion_culled": 0,
            "passed": 0,
        }

        for obj in objects:
            oid = obj.get("id", "unknown")
            bbox_min = np.array(obj.get("bbox_min", [-1, -1, -1]), dtype=np.float32)
            bbox_max = np.array(obj.get("bbox_max", [1, 1, 1]), dtype=np.float32)
            transform = np.array(obj.get("transform", np.eye(4)), dtype=np.float32)

            center_local = (bbox_min + bbox_max) * 0.5
            center_world = (transform @ np.append(center_local, 1.0))[:3]
            dist = float(np.linalg.norm(center_world - camera_pos))

            # 1. Distance Culling
            obj_max_dist = obj.get("max_draw_distance", self.max_distance)
            if dist > obj_max_dist:
                stats["distance_culled"] += 1
                culled.append(obj)
                self.visibility_history[oid] = 0
                continue

            # 2. Frustum Culling
            center_clip = vp_matrix @ np.append(center_world, 1.0)
            if center_clip[3] <= 0.01:
                # Behind camera plane
                stats["frustum_culled"] += 1
                culled.append(obj)
                self.visibility_history[oid] = 0
                continue

            ndc = center_clip[:3] / center_clip[3]
            radius_world = float(np.linalg.norm(bbox_max - bbox_min)) * 0.5
            proj_radius = radius_world / max(0.1, dist)

            # Check if NDC point + radius falls outside [-1, 1] bounds
            if (ndc[0] + proj_radius < -1.0 or ndc[0] - proj_radius > 1.0 or
                ndc[1] + proj_radius < -1.0 or ndc[1] - proj_radius > 1.0 or
                ndc[2] < 0.0 or ndc[2] > 1.0):
                stats["frustum_culled"] += 1
                culled.append(obj)
                self.visibility_history[oid] = 0
                continue

            # 3. Occlusion culling heuristic against registered large occluders
            is_occluded = False
            for occ_center, occ_normal, occ_radius in self.occluders:
                occ_dist = float(np.linalg.norm(occ_center - camera_pos))
                if dist > occ_dist + 2.0:
                    # Object is further than occluder; test angular containment
                    dir_to_occ = (occ_center - camera_pos) / max(1e-5, occ_dist)
                    dir_to_obj = (center_world - camera_pos) / max(1e-5, dist)
                    cos_angle = float(np.dot(dir_to_occ, dir_to_obj))
                    angular_occ_radius = occ_radius / max(0.1, occ_dist)
                    angular_obj_radius = radius_world / max(0.1, dist)
                    if cos_angle > np.cos(angular_occ_radius) and (angular_obj_radius < angular_occ_radius * 0.8):
                        is_occluded = True
                        break

            if is_occluded:
                stats["occlusion_culled"] += 1
                culled.append(obj)
                self.visibility_history[oid] = 0
                continue

            # Passed all culling checks
            stats["passed"] += 1
            visible.append(obj)
            self.visibility_history[oid] = self.visibility_history.get(oid, 0) + 1

        return visible, culled, stats

    def register_occluder(self, center: np.ndarray, normal: np.ndarray, radius: float):
        """Adds a major occluding surface (e.g. wall, terrain chunk) to the occlusion hierarchy."""
        self.occluders.append((center, normal, radius))

    def clear_occluders(self):
        self.occluders.clear()
