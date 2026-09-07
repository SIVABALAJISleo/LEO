"""
cbe/state/object_state.py
Per-object dynamic tracking, motion state, visibility, and cryptographic state hashing.
"""

from __future__ import annotations

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ObjectState:
    object_id: str
    name: str = "object"
    position: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32))  # Quaternion (x, y, z, w)
    scale: np.ndarray = field(default_factory=lambda: np.ones(3, dtype=np.float32))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    
    # Material & Shader Profile
    material_id: str = "default_diffuse"
    material_hash: str = "0"
    is_static: bool = False
    is_transparent: bool = False
    semantic_class: str = "environment"  # "character", "ui", "foliage", "particle", "environment"
    
    # State tracking
    importance_weight: float = 1.0
    history_confidence: float = 1.0
    prediction_confidence: float = 1.0
    visibility_state: bool = True
    state_hash: str = ""

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_state_hash()

    def compute_state_hash(self) -> str:
        """Computes deterministic 64-bit state hash from transform, kinematics, and material."""
        h = hashlib.blake2b(digest_size=8)
        h.update(self.object_id.encode("utf-8"))
        h.update(np.round(self.position, 4).tobytes())
        h.update(np.round(self.rotation, 4).tobytes())
        h.update(np.round(self.scale, 4).tobytes())
        h.update(self.material_id.encode("utf-8"))
        h.update(self.material_hash.encode("utf-8"))
        h.update(b"1" if self.visibility_state else b"0")
        self.state_hash = h.hexdigest()
        return self.state_hash

    def update_transform(self, pos: np.ndarray, rot: Optional[np.ndarray] = None, dt: float = 0.01667):
        """Updates transform and calculates kinematic velocity."""
        old_pos = self.position.copy()
        self.position = np.asarray(pos, dtype=np.float32)
        if rot is not None:
            self.rotation = np.asarray(rot, dtype=np.float32)
        if dt > 1e-5:
            self.velocity = (self.position - old_pos) / dt
        self.compute_state_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "name": self.name,
            "position": self.position.tolist(),
            "rotation": self.rotation.tolist(),
            "scale": self.scale.tolist(),
            "velocity": self.velocity.tolist(),
            "material_id": self.material_id,
            "is_static": self.is_static,
            "semantic_class": self.semantic_class,
            "importance_weight": self.importance_weight,
            "history_confidence": self.history_confidence,
            "prediction_confidence": self.prediction_confidence,
            "state_hash": self.state_hash,
        }
