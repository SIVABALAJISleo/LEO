"""
hyper/work_analyzer/analyzer.py
===============================
HYPER Work Analyzer:
Decomposes workloads and scene states into:
- WorkGraph & DependencyGraph
- CostMap (per-region / per-object computational cost)
- VisibilityMap (frustum, occlusion, distance)
- ImportanceMap (spatial & semantic importance)
- ChangeMap (delta detection against previous state)
- UncertaintyMap (per-pixel / per-region confidence)
- ReuseMap (temporal & spatial cache candidate regions)
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class SceneObject:
    """Represents an active object within a 3D scene."""
    object_id: str
    name: str
    category: str  # 'player', 'weapon', 'enemy', 'interactive', 'geometry', 'background', 'sky'
    transform: np.ndarray  # 4x4 matrix
    mesh_hash: str
    material_hash: str
    bounding_box_min: np.ndarray  # (3,)
    bounding_box_max: np.ndarray  # (3,)
    vertex_count: int
    is_static: bool = False
    is_transparent: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CameraState:
    """Represents camera view parameters."""
    position: np.ndarray  # (3,)
    forward: np.ndarray   # (3,)
    up: np.ndarray        # (3,)
    view_matrix: np.ndarray  # 4x4
    proj_matrix: np.ndarray  # 4x4
    fov_degrees: float = 90.0
    near_plane: float = 0.1
    far_plane: float = 1000.0


@dataclass
class LightState:
    """Represents a light source in the scene."""
    light_id: str
    light_type: str  # 'directional', 'point', 'spot'
    position: np.ndarray
    direction: np.ndarray
    color: np.ndarray
    intensity: float
    is_static: bool = True


@dataclass
class WorkAnalysisResult:
    """Structured output of the HYPER Work Analyzer."""
    frame_id: int
    timestamp: float
    total_objects: int
    visible_objects: int
    changed_objects: int
    reusable_objects: int
    cost_map: np.ndarray            # (H_grid, W_grid) estimated relative cost
    visibility_map: np.ndarray      # (H_grid, W_grid) bool visibility
    importance_map: np.ndarray      # (H_grid, W_grid) float [0, 1]
    change_map: np.ndarray          # (H_grid, W_grid) float [0, 1] rate of change
    uncertainty_map: np.ndarray     # (H_grid, W_grid) float [0, 1]
    reuse_map: np.ndarray           # (H_grid, W_grid) bool can reuse
    work_graph: Dict[str, List[str]]
    dependency_graph: Dict[str, List[str]]
    elimination_opportunities: List[str]
    analysis_latency_ms: float


class HyperWorkAnalyzer:
    """
    Analyzes scene state, geometry, materials, lighting, camera, and history to
    determine the MINIMUM required computation before rendering begins.
    """

    def __init__(self, grid_res: Tuple[int, int] = (60, 80)):
        self.grid_h, self.grid_w = grid_res
        self.previous_objects: Dict[str, SceneObject] = {}
        self.previous_camera: Optional[CameraState] = None
        self.previous_lights: Dict[str, LightState] = {}
        self.frame_counter = 0

    def analyze_scene(
        self,
        objects: List[SceneObject],
        camera: CameraState,
        lights: List[LightState],
        history_confidence: Optional[np.ndarray] = None,
    ) -> WorkAnalysisResult:
        """
        Full scene work analysis pass:
        1. Frustum & distance visibility testing
        2. Delta change detection vs previous frame
        3. Importance map generation based on category, distance, and screen coverage
        4. Uncertainty estimation based on motion, lighting deltas, and disocclusion
        5. WorkGraph & DependencyGraph generation
        """
        t0 = time.perf_counter()
        self.frame_counter += 1

        cost_map = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        visibility_map = np.zeros((self.grid_h, self.grid_w), dtype=bool)
        importance_map = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        change_map = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        uncertainty_map = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        reuse_map = np.zeros((self.grid_h, self.grid_w), dtype=bool)

        current_obj_dict = {obj.object_id: obj for obj in objects}
        visible_obj_count = 0
        changed_obj_count = 0
        reusable_obj_count = 0

        work_graph: Dict[str, List[str]] = {}
        dependency_graph: Dict[str, List[str]] = {}
        elimination_opportunities = []

        # Check camera movement delta
        camera_moved = True
        if self.previous_camera is not None:
            cam_pos_delta = np.linalg.norm(camera.position - self.previous_camera.position)
            cam_view_delta = np.linalg.norm(camera.forward - self.previous_camera.forward)
            camera_moved = (cam_pos_delta > 1e-4) or (cam_view_delta > 1e-4)
        if not camera_moved:
            elimination_opportunities.append("Camera stationary: static geometry and background shading eligible for 100% temporal reuse.")

        # Analyze each object
        vp_matrix = camera.proj_matrix @ camera.view_matrix
        for obj in objects:
            # 1. Transform bounding box center to NDC
            center_local = (obj.bounding_box_min + obj.bounding_box_max) * 0.5
            center_world = (obj.transform @ np.append(center_local, 1.0))[:3]
            center_clip = vp_matrix @ np.append(center_world, 1.0)
            
            # Distance from camera
            dist = float(np.linalg.norm(center_world - camera.position))
            
            # Simple Frustum Check (w > 0 and within [-1, 1] with margin)
            is_visible = False
            screen_x, screen_y = 0.5, 0.5
            screen_radius = 0.1
            if center_clip[3] > 0.1:
                ndc_x = center_clip[0] / center_clip[3]
                ndc_y = center_clip[1] / center_clip[3]
                radius_world = float(np.linalg.norm(obj.bounding_box_max - obj.bounding_box_min)) * 0.5
                screen_radius = max(0.01, min(0.5, radius_world / max(0.1, dist)))
                if -1.5 <= ndc_x <= 1.5 and -1.5 <= ndc_y <= 1.5:
                    is_visible = True
                    screen_x = np.clip((ndc_x + 1.0) * 0.5, 0.0, 1.0)
                    screen_y = np.clip((ndc_y + 1.0) * 0.5, 0.0, 1.0)

            if not is_visible:
                elimination_opportunities.append(f"Frustum culling eliminated object '{obj.name}' ({obj.vertex_count} vertices).")
                continue

            visible_obj_count += 1

            # 2. Change Detection
            has_changed = True
            if obj.object_id in self.previous_objects:
                prev_obj = self.previous_objects[obj.object_id]
                trans_diff = np.max(np.abs(obj.transform - prev_obj.transform))
                mesh_diff = obj.mesh_hash != prev_obj.mesh_hash
                mat_diff = obj.material_hash != prev_obj.material_hash
                has_changed = (trans_diff > 1e-4) or mesh_diff or mat_diff

            if has_changed:
                changed_obj_count += 1
            else:
                reusable_obj_count += 1

            # 3. Splat object properties onto spatial grid
            grid_center_x = int(screen_x * (self.grid_w - 1))
            grid_center_y = int(screen_y * (self.grid_h - 1))
            r_x = max(1, int(screen_radius * self.grid_w))
            r_y = max(1, int(screen_radius * self.grid_h))

            y_min = max(0, grid_center_y - r_y)
            y_max = min(self.grid_h, grid_center_y + r_y + 1)
            x_min = max(0, grid_center_x - r_x)
            x_max = min(self.grid_w, grid_center_x + r_x + 1)

            # Determine category base importance
            category_weights = {
                "player": 1.0,
                "weapon": 1.0,
                "enemy": 0.95,
                "interactive": 0.90,
                "geometry": 0.70,
                "background": 0.35,
                "sky": 0.15,
            }
            base_importance = category_weights.get(obj.category, 0.5)
            # Distance attenuation
            distance_factor = float(np.clip(1.0 - (dist / camera.far_plane), 0.1, 1.0))
            obj_importance = base_importance * distance_factor

            # Estimated cost proportional to vertex count & screen area
            obj_cost = (obj.vertex_count / 1000.0) * (screen_radius ** 2)

            # Rasterize to grids
            visibility_map[y_min:y_max, x_min:x_max] = True
            importance_map[y_min:y_max, x_min:x_max] = np.maximum(
                importance_map[y_min:y_max, x_min:x_max], obj_importance
            )
            cost_map[y_min:y_max, x_min:x_max] += obj_cost
            if has_changed or camera_moved:
                change_map[y_min:y_max, x_min:x_max] = np.maximum(
                    change_map[y_min:y_max, x_min:x_max], 1.0 if has_changed else 0.5
                )

            # Build dependency and work graph entries
            work_graph[obj.object_id] = [f"mesh_{obj.mesh_hash[:8]}", f"mat_{obj.material_hash[:8]}"]
            dependency_graph[obj.object_id] = [light.light_id for light in lights if np.linalg.norm(light.position - center_world) < 20.0]

        # Calculate uncertainty map
        # Uncertainty is high where change is high and history confidence is low
        if history_confidence is not None and history_confidence.shape == (self.grid_h, self.grid_w):
            uncertainty_map = np.clip(change_map * 0.7 + (1.0 - history_confidence) * 0.3, 0.0, 1.0)
        else:
            uncertainty_map = np.clip(change_map, 0.0, 1.0)

        # Reuse map is valid where visible, unchanged, and low uncertainty
        reuse_map = visibility_map & (uncertainty_map < 0.25) & (change_map < 0.1)

        # Update historical state
        self.previous_objects = current_obj_dict
        self.previous_camera = camera
        self.previous_lights = {l.light_id: l for l in lights}

        t_elapsed = (time.perf_counter() - t0) * 1000.0

        return WorkAnalysisResult(
            frame_id=self.frame_counter,
            timestamp=time.time(),
            total_objects=len(objects),
            visible_objects=visible_obj_count,
            changed_objects=changed_obj_count,
            reusable_objects=reusable_obj_count,
            cost_map=cost_map,
            visibility_map=visibility_map,
            importance_map=importance_map,
            change_map=change_map,
            uncertainty_map=uncertainty_map,
            reuse_map=reuse_map,
            work_graph=work_graph,
            dependency_graph=dependency_graph,
            elimination_opportunities=elimination_opportunities,
            analysis_latency_ms=round(t_elapsed, 3),
        )
