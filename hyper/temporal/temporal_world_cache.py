"""
hyper/temporal/temporal_world_cache.py
======================================
HYPER Temporal World Cache:
Contains specialized caches for frames, depth, motion, lighting, visibility,
materials, geometry, and objects.
Every cached entry tracks timestamp, dependencies, validity, confidence, and invalidation rules.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class CacheEntry:
    """Rigorous metadata wrapper for any temporally cached resource."""
    entry_id: str
    frame_id: int
    timestamp: float
    data: Any
    confidence: float                  # [0.0, 1.0]
    is_valid: bool = True
    dependencies: List[str] = field(default_factory=list)
    invalidation_conditions: Dict[str, Any] = field(default_factory=dict)

    def invalidate(self, reason: str = ""):
        self.is_valid = False
        self.confidence = 0.0


class TemporalFrameCache:
    """Maintains color buffer history with confidence map."""
    def __init__(self, capacity: int = 4):
        self.capacity = capacity
        self.frames: List[CacheEntry] = []

    def store_frame(self, frame_id: int, color_buffer: np.ndarray, confidence: float = 1.0):
        entry = CacheEntry(
            entry_id=f"frame_{frame_id}",
            frame_id=frame_id,
            timestamp=time.time(),
            data=color_buffer.copy(),
            confidence=confidence,
        )
        self.frames.insert(0, entry)
        if len(self.frames) > self.capacity:
            self.frames.pop()

    def get_latest(self) -> Optional[CacheEntry]:
        for f in self.frames:
            if f.is_valid:
                return f
        return None


class TemporalDepthCache:
    """Caches linear depth buffers for disocclusion testing."""
    def __init__(self):
        self.current_depth: Optional[CacheEntry] = None
        self.previous_depth: Optional[CacheEntry] = None

    def update(self, frame_id: int, depth_map: np.ndarray):
        self.previous_depth = self.current_depth
        self.current_depth = CacheEntry(
            entry_id=f"depth_{frame_id}",
            frame_id=frame_id,
            timestamp=time.time(),
            data=depth_map.copy(),
            confidence=1.0,
        )


class TemporalMotionCache:
    """Caches 2D screen-space pixel motion vectors (dx, dy)."""
    def __init__(self):
        self.motion_entry: Optional[CacheEntry] = None

    def update(self, frame_id: int, motion_vectors: np.ndarray):
        self.motion_entry = CacheEntry(
            entry_id=f"motion_{frame_id}",
            frame_id=frame_id,
            timestamp=time.time(),
            data=motion_vectors.copy(),
            confidence=1.0,
        )


class TemporalLightingCache:
    """Caches direct and indirect illumination grids."""
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}

    def store(self, grid_id: str, frame_id: int, lighting_data: np.ndarray, light_deps: List[str]):
        self.cache[grid_id] = CacheEntry(
            entry_id=grid_id,
            frame_id=frame_id,
            timestamp=time.time(),
            data=lighting_data,
            confidence=1.0,
            dependencies=light_deps,
        )

    def invalidate_by_light(self, modified_light_id: str):
        for entry in self.cache.values():
            if modified_light_id in entry.dependencies:
                entry.invalidate(f"Light {modified_light_id} modified")


class TemporalVisibilityCache:
    """Tracks per-object visibility duration and occluder relationships."""
    def __init__(self):
        self.object_visibility: Dict[str, CacheEntry] = {}

    def update_visibility(self, object_id: str, frame_id: int, is_visible: bool):
        prev = self.object_visibility.get(object_id)
        conf = min(1.0, (prev.confidence + 0.2)) if (prev and is_visible) else (1.0 if is_visible else 0.0)
        self.object_visibility[object_id] = CacheEntry(
            entry_id=object_id,
            frame_id=frame_id,
            timestamp=time.time(),
            data=is_visible,
            confidence=conf,
            is_valid=is_visible,
        )


class TemporalMaterialCache:
    """Caches compiled shader pipeline states and material bindings."""
    def __init__(self):
        self.pso_cache: Dict[str, CacheEntry] = {}

    def get_or_create(self, mat_hash: str, frame_id: int, factory_fn) -> Any:
        if mat_hash in self.pso_cache and self.pso_cache[mat_hash].is_valid:
            return self.pso_cache[mat_hash].data
        compiled = factory_fn()
        self.pso_cache[mat_hash] = CacheEntry(
            entry_id=mat_hash,
            frame_id=frame_id,
            timestamp=time.time(),
            data=compiled,
            confidence=1.0,
        )
        return compiled


class TemporalGeometryCache:
    """Caches transformed vertex buffers, BVH bounding volumes, and instance matrices."""
    def __init__(self):
        self.geom_cache: Dict[str, CacheEntry] = {}

    def store_mesh(self, mesh_id: str, frame_id: int, bvh_or_vbo: Any, is_static: bool):
        self.geom_cache[mesh_id] = CacheEntry(
            entry_id=mesh_id,
            frame_id=frame_id,
            timestamp=time.time(),
            data=bvh_or_vbo,
            confidence=1.0,
            is_valid=True,
            invalidation_conditions={"is_static": is_static},
        )


class TemporalObjectCache:
    """Unified container orchestrating all specialized temporal caches."""
    def __init__(self):
        self.frames = TemporalFrameCache()
        self.depth = TemporalDepthCache()
        self.motion = TemporalMotionCache()
        self.lighting = TemporalLightingCache()
        self.visibility = TemporalVisibilityCache()
        self.materials = TemporalMaterialCache()
        self.geometry = TemporalGeometryCache()

    def invalidate_all(self, reason: str = "Scene reset"):
        """Forces full cache invalidation on camera teleport or major disruption."""
        for entry in self.frames.frames:
            entry.invalidate(reason)
