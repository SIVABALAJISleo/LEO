"""
hyper/world_state/world_state.py
================================
HYPER World State:
Persistent state representation tracking dynamic scene evolution across frames.
Calculates ΔWorld = CurrentWorld - PreviousWorld to avoid treating frames as de novo.
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class DeltaWorld:
    """Represents the exact differential changes between two world states."""
    frame_id: int
    delta_time: float
    camera_delta_position: float
    camera_delta_angle: float
    changed_object_ids: List[str]
    added_object_ids: List[str]
    removed_object_ids: List[str]
    changed_light_ids: List[str]
    mesh_invalidation_count: int
    material_invalidation_count: int
    global_change_ratio: float  # [0, 1] percentage of world modified
    requires_full_flush: bool


class HyperWorldState:
    """
    Persistent World State Engine:
    Maintains active frame history, geometry hashes, lighting state,
    motion vectors, depth history, and calculates ΔWorld.
    """

    def __init__(self, buffer_h: int = 1080, buffer_w: int = 1920):
        self.buffer_h = buffer_h
        self.buffer_w = buffer_w
        self.current_frame_id = 0
        self.last_update_timestamp = time.perf_counter()

        # Object registry: id -> dict of attributes
        self.objects: Dict[str, Dict[str, Any]] = {}
        self.prev_objects: Dict[str, Dict[str, Any]] = {}

        # Camera state
        self.camera: Optional[Dict[str, Any]] = None
        self.prev_camera: Optional[Dict[str, Any]] = None

        # Lighting state: id -> dict
        self.lights: Dict[str, Dict[str, Any]] = {}
        self.prev_lights: Dict[str, Dict[str, Any]] = {}

        # Frame buffers: L1 Active Frame, L2 History (ping-pong)
        self.active_frame: Optional[np.ndarray] = None          # (H, W, 3) float32
        self.previous_frame: Optional[np.ndarray] = None        # (H, W, 3) float32
        self.prev_prev_frame: Optional[np.ndarray] = None       # (H, W, 3) float32

        # Motion vectors: (H, W, 2) float32 (screen space offset in pixels)
        self.motion_vectors: Optional[np.ndarray] = None
        
        # Depth buffers: (H, W) float32
        self.current_depth: Optional[np.ndarray] = None
        self.previous_depth: Optional[np.ndarray] = None

        # Temporal confidence & importance maps: (H, W) float32
        self.temporal_confidence: np.ndarray = np.zeros((buffer_h, buffer_w), dtype=np.float32)
        self.importance_history: np.ndarray = np.zeros((buffer_h, buffer_w), dtype=np.float32)

        # Resource residency & memory pressure tracking
        self.resident_textures: Dict[str, int] = {}  # texture_id -> size_bytes
        self.resident_geometry: Dict[str, int] = {}  # mesh_id -> vertex_bytes
        self.memory_pressure_ratio: float = 0.1      # fraction of budget used

    def update_frame(
        self,
        new_objects: Dict[str, Dict[str, Any]],
        new_camera: Dict[str, Any],
        new_lights: Dict[str, Dict[str, Any]],
        motion_vectors: Optional[np.ndarray] = None,
        depth_buffer: Optional[np.ndarray] = None,
    ) -> DeltaWorld:
        """
        Ingests the current frame world description, computes ΔWorld,
        and rotates historical buffers.
        """
        t_now = time.perf_counter()
        dt = t_now - self.last_update_timestamp
        self.last_update_timestamp = t_now
        self.current_frame_id += 1

        # Calculate camera delta
        cam_pos_delta = 0.0
        cam_angle_delta = 0.0
        if self.camera is not None and new_camera is not None:
            cam_pos_delta = float(np.linalg.norm(
                np.array(new_camera.get("position", [0, 0, 0])) -
                np.array(self.camera.get("position", [0, 0, 0]))
            ))
            # Directional alignment dot product
            dir_new = np.array(new_camera.get("forward", [0, 0, 1]))
            dir_old = np.array(self.camera.get("forward", [0, 0, 1]))
            cos_theta = float(np.clip(np.dot(dir_new, dir_old), -1.0, 1.0))
            cam_angle_delta = float(np.degrees(np.arccos(cos_theta)))

        # Calculate object changes
        curr_keys = set(new_objects.keys())
        prev_keys = set(self.objects.keys())

        added_ids = list(curr_keys - prev_keys)
        removed_ids = list(prev_keys - curr_keys)
        common_ids = curr_keys & prev_keys

        changed_ids = []
        mesh_invalidations = 0
        mat_invalidations = 0

        for oid in common_ids:
            cur = new_objects[oid]
            prv = self.objects[oid]
            # Check transform diff
            t_diff = float(np.max(np.abs(
                np.array(cur.get("transform", np.eye(4))) -
                np.array(prv.get("transform", np.eye(4)))
            )))
            mesh_diff = cur.get("mesh_hash") != prv.get("mesh_hash")
            mat_diff = cur.get("material_hash") != prv.get("material_hash")

            if t_diff > 1e-4 or mesh_diff or mat_diff:
                changed_ids.append(oid)
            if mesh_diff:
                mesh_invalidations += 1
            if mat_diff:
                mat_invalidations += 1

        # Calculate light changes
        changed_light_ids = []
        for lid, light in new_lights.items():
            if lid in self.lights:
                prv_light = self.lights[lid]
                pos_diff = float(np.linalg.norm(
                    np.array(light.get("position", [0, 0, 0])) -
                    np.array(prv_light.get("position", [0, 0, 0]))
                ))
                int_diff = abs(light.get("intensity", 1.0) - prv_light.get("intensity", 1.0))
                if pos_diff > 1e-3 or int_diff > 1e-3:
                    changed_light_ids.append(lid)
            else:
                changed_light_ids.append(lid)

        total_tracked = max(1, len(curr_keys))
        change_ratio = (len(changed_ids) + len(added_ids) + len(removed_ids)) / float(total_tracked)
        
        # Invalidation threshold: if camera moved violently (>45 deg) or >80% world changed, flush
        requires_flush = (cam_angle_delta > 45.0) or (change_ratio > 0.8)

        # Rotate historical states
        self.prev_prev_frame = self.previous_frame.copy() if self.previous_frame is not None else None
        self.previous_frame = self.active_frame.copy() if self.active_frame is not None else None
        self.previous_depth = self.current_depth.copy() if self.current_depth is not None else None

        self.prev_objects = self.objects
        self.objects = new_objects
        self.prev_camera = self.camera
        self.camera = new_camera
        self.prev_lights = self.lights
        self.lights = new_lights

        if depth_buffer is not None:
            self.current_depth = depth_buffer
        if motion_vectors is not None:
            self.motion_vectors = motion_vectors

        # Decay or update confidence
        if requires_flush:
            self.temporal_confidence.fill(0.0)
        else:
            self.temporal_confidence = np.clip(self.temporal_confidence * 0.95 + 0.05, 0.0, 1.0)

        delta = DeltaWorld(
            frame_id=self.current_frame_id,
            delta_time=dt,
            camera_delta_position=cam_pos_delta,
            camera_delta_angle=cam_angle_delta,
            changed_object_ids=changed_ids,
            added_object_ids=added_ids,
            removed_object_ids=removed_ids,
            changed_light_ids=changed_light_ids,
            mesh_invalidation_count=mesh_invalidations,
            material_invalidation_count=mat_invalidations,
            global_change_ratio=round(change_ratio, 4),
            requires_full_flush=requires_flush,
        )

        return delta

    def set_active_frame(self, frame_buffer: np.ndarray):
        """Stores the newly completed active rendered/reconstructed frame."""
        self.active_frame = frame_buffer
