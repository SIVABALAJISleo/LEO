"""
cbe/state/scene_state.py
Persistent scene-state engine tracking camera, geometry, materials, lighting,
depth, and cryptographic state hashing to eliminate redundant frame computation.
"""

from __future__ import annotations

import hashlib
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from .object_state import ObjectState


@dataclass
class CameraState:
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))
    target: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 1.0], dtype=np.float32))
    up: np.ndarray = field(default_factory=lambda: np.array([0.0, 1.0, 0.0], dtype=np.float32))
    fov_degrees: float = 60.0
    aspect_ratio: float = 16.0 / 9.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    jitter_offset: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float32))  # Subpixel jitter [-0.5, 0.5]
    
    view_matrix: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))
    proj_matrix: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))
    view_proj_matrix: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))
    prev_view_proj_matrix: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float32))

    def __post_init__(self):
        self.update_matrices()

    def update_matrices(self):
        """Builds standard LookAt and Perspective matrices."""
        # Forward vector
        f = self.target - self.position
        fn = np.linalg.norm(f)
        if fn > 1e-6:
            f /= fn
        else:
            f = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        # Right vector
        r = np.cross(f, self.up)
        rn = np.linalg.norm(r)
        if rn > 1e-6:
            r /= rn
        else:
            r = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        # Recalculate true up
        u = np.cross(r, f)

        # View matrix
        vm = np.eye(4, dtype=np.float32)
        vm[0, :3] = r
        vm[1, :3] = u
        vm[2, :3] = f
        vm[0, 3] = -np.dot(r, self.position)
        vm[1, 3] = -np.dot(u, self.position)
        vm[2, 3] = -np.dot(f, self.position)
        self.view_matrix = vm

        # Perspective projection
        fov_rad = np.radians(self.fov_degrees)
        tan_half = np.tan(fov_rad / 2.0)
        pm = np.zeros((4, 4), dtype=np.float32)
        pm[0, 0] = 1.0 / (self.aspect_ratio * tan_half)
        pm[1, 1] = 1.0 / tan_half
        pm[2, 2] = (self.far_plane + self.near_plane) / (self.far_plane - self.near_plane)
        pm[2, 3] = -(2.0 * self.far_plane * self.near_plane) / (self.far_plane - self.near_plane)
        pm[3, 2] = 1.0
        self.proj_matrix = pm

        # Save previous and update current
        self.prev_view_proj_matrix = self.view_proj_matrix.copy()
        self.view_proj_matrix = np.matmul(self.proj_matrix, self.view_matrix)

    def compute_hash(self) -> str:
        h = hashlib.blake2b(digest_size=8)
        h.update(np.round(self.position, 4).tobytes())
        h.update(np.round(self.target, 4).tobytes())
        h.update(np.round(self.jitter_offset, 4).tobytes())
        return h.hexdigest()


@dataclass
class LightState:
    light_id: str
    light_type: str = "directional"  # "directional", "point", "spot"
    position: np.ndarray = field(default_factory=lambda: np.array([10.0, 20.0, 10.0], dtype=np.float32))
    direction: np.ndarray = field(default_factory=lambda: np.array([0.577, -0.577, 0.577], dtype=np.float32))
    intensity: float = 1.0
    color: np.ndarray = field(default_factory=lambda: np.ones(3, dtype=np.float32))
    cast_shadows: bool = True

    def compute_hash(self) -> str:
        h = hashlib.blake2b(digest_size=8)
        h.update(self.light_id.encode("utf-8"))
        h.update(np.round(self.position, 3).tobytes())
        h.update(np.round(self.direction, 3).tobytes())
        h.update(f"{self.intensity:.3f}".encode("utf-8"))
        return h.hexdigest()


@dataclass
class SceneState:
    frame_index: int = 0
    timestamp: float = field(default_factory=time.time)
    camera: CameraState = field(default_factory=CameraState)
    objects: Dict[str, ObjectState] = field(default_factory=dict)
    lights: Dict[str, LightState] = field(default_factory=dict)
    environment_radiance: np.ndarray = field(default_factory=lambda: np.array([0.1, 0.15, 0.2], dtype=np.float32))
    
    scene_hash: str = ""
    camera_hash: str = ""
    lighting_hash: str = ""
    
    def __post_init__(self):
        self.compute_scene_hash()

    def add_object(self, obj: ObjectState):
        self.objects[obj.object_id] = obj
        self.compute_scene_hash()

    def add_light(self, light: LightState):
        self.lights[light.light_id] = light
        self.compute_scene_hash()

    def compute_scene_hash(self) -> str:
        """Computes comprehensive hierarchical cryptographic scene hash."""
        self.camera_hash = self.camera.compute_hash()
        
        lh = hashlib.blake2b(digest_size=8)
        for l_id in sorted(self.lights.keys()):
            lh.update(self.lights[l_id].compute_hash().encode("utf-8"))
        self.lighting_hash = lh.hexdigest()

        sh = hashlib.blake2b(digest_size=8)
        sh.update(self.camera_hash.encode("utf-8"))
        sh.update(self.lighting_hash.encode("utf-8"))
        sh.update(np.round(self.environment_radiance, 3).tobytes())
        for o_id in sorted(self.objects.keys()):
            sh.update(self.objects[o_id].compute_state_hash().encode("utf-8"))
            
        self.scene_hash = sh.hexdigest()
        return self.scene_hash

    def diff(self, previous: Optional[SceneState]) -> Dict[str, Any]:
        """
        Analyzes delta between current state and historical state.
        Returns exact change lists and bypass recommendation.
        """
        if previous is None:
            return {
                "identical": False,
                "camera_moved": True,
                "lighting_changed": True,
                "camera_delta_norm": 999.0,
                "changed_objects": list(self.objects.keys()),
                "bypass_possible": False,
                "strategy_hint": "FULL_RENDER",
            }

        camera_moved = self.camera_hash != previous.camera_hash
        lighting_changed = self.lighting_hash != previous.lighting_hash
        identical = self.scene_hash == previous.scene_hash
        
        cam_delta = np.linalg.norm(self.camera.position - previous.camera.position)
        
        changed_objs: List[str] = []
        for o_id, obj in self.objects.items():
            if o_id not in previous.objects:
                changed_objs.append(o_id)
            elif obj.state_hash != previous.objects[o_id].state_hash:
                changed_objs.append(o_id)
                
        for o_id in previous.objects:
            if o_id not in self.objects:
                changed_objs.append(o_id)

        # Classify bypass viability
        if identical:
            strategy = "EXACT_REUSE"  # Tier 0 (0 compute)
        elif not camera_moved and not lighting_changed and len(changed_objs) == 0:
            strategy = "EXACT_REUSE"
        elif camera_moved and not lighting_changed and len(changed_objs) == 0:
            strategy = "TEMPORAL_REPROJECTION"  # Tier 1
        elif len(changed_objs) < len(self.objects) * 0.3:
            strategy = "SPARSE_RESIDUAL"  # Tier 4
        else:
            strategy = "ADAPTIVE_RECONSTRUCTION"  # Tier 3

        return {
            "identical": identical,
            "camera_moved": camera_moved,
            "lighting_changed": lighting_changed,
            "camera_delta_norm": float(cam_delta),
            "changed_objects": changed_objs,
            "changed_object_count": len(changed_objs),
            "total_object_count": len(self.objects),
            "bypass_possible": identical or strategy in ("EXACT_REUSE", "TEMPORAL_REPROJECTION"),
            "strategy_hint": strategy,
        }
