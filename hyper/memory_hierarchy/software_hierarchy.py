"""
hyper/memory_hierarchy/software_hierarchy.py
============================================
HYPER Software Memory Hierarchy:
Logical multi-tier cache memory system designed to minimize memory traffic,
recomputation, and bus contention on shared CPU+iGPU unified memory.

Tiers:
- L1 (Active Frame): Zero-copy resident hot render buffers in CPU cache / unified RAM.
- L2 (Recent Frame History): Ping-pong historical color, depth, and motion buffers.
- L3 (Scene Cache): Static geometry BVH, compiled shader PSOs, and material textures.
- L4 (Compressed World State): Quantized / entropy-compressed past world snapshots.
- L5 (Disk-backed Cold Cache): Serialized offline assets, irradiance probes, and holdout caches.

NOTE: This is a software memory hierarchy designed to manage data locality and minimize
unnecessary memory transfers. It does NOT physically create additional VRAM.
"""

import os
import time
import zlib
import pickle
from typing import Any, Dict, Optional, Tuple
import numpy as np


class SoftwareMemoryHierarchy:
    """
    Manages structured memory tiers L1 through L5.
    """

    def __init__(self, cold_cache_dir: str = ".hyper_cache"):
        self.cold_cache_dir = cold_cache_dir
        os.makedirs(self.cold_cache_dir, exist_ok=True)

        # L1: Hot Active Frame Buffers
        self.l1_active_frame: Optional[np.ndarray] = None
        self.l1_active_depth: Optional[np.ndarray] = None
        self.l1_active_motion: Optional[np.ndarray] = None

        # L2: Recent Frame History (ping-pong ring buffer)
        self.l2_history_frames: Dict[int, np.ndarray] = {}
        self.l2_history_depths: Dict[int, np.ndarray] = {}

        # L3: Scene Cache (Geometry, Materials, Shaders)
        self.l3_scene_cache: Dict[str, Any] = {}

        # L4: Compressed World State (zlib compressed blobs in RAM)
        self.l4_compressed_states: Dict[str, bytes] = {}

        # L5: Disk-backed persistent cache tracker
        self.l5_disk_keys: Dict[str, str] = {}

    # --- L1 Active Frame ---
    def set_l1_active(self, color: np.ndarray, depth: Optional[np.ndarray] = None, motion: Optional[np.ndarray] = None):
        self.l1_active_frame = color
        self.l1_active_depth = depth
        self.l1_active_motion = motion

    # --- L2 Frame History ---
    def store_l2_history(self, frame_id: int, color: np.ndarray, depth: Optional[np.ndarray] = None):
        self.l2_history_frames[frame_id] = color.copy()
        if depth is not None:
            self.l2_history_depths[frame_id] = depth.copy()
        # Keep only last 4 frames in L2
        if len(self.l2_history_frames) > 4:
            oldest = min(self.l2_history_frames.keys())
            # Compress and demote to L4
            self.demote_to_l4(f"frame_{oldest}", self.l2_history_frames.pop(oldest))
            if oldest in self.l2_history_depths:
                self.l2_history_depths.pop(oldest)

    def get_l2_frame(self, frame_id: int) -> Optional[np.ndarray]:
        return self.l2_history_frames.get(frame_id)

    # --- L3 Scene Cache ---
    def put_l3(self, key: str, data: Any):
        self.l3_scene_cache[key] = data

    def get_l3(self, key: str) -> Optional[Any]:
        return self.l3_scene_cache.get(key)

    # --- L4 Compressed World State ---
    def demote_to_l4(self, key: str, data: Any):
        try:
            raw_bytes = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            compressed = zlib.compress(raw_bytes, level=1)  # fast compression
            self.l4_compressed_states[key] = compressed
            # Limit L4 to 16 compressed states
            if len(self.l4_compressed_states) > 16:
                oldest_key = next(iter(self.l4_compressed_states.keys()))
                self.demote_to_l5(oldest_key, self.l4_compressed_states.pop(oldest_key))
        except Exception:
            pass

    def get_l4(self, key: str) -> Optional[Any]:
        if key in self.l4_compressed_states:
            raw = zlib.decompress(self.l4_compressed_states[key])
            return pickle.loads(raw)
        return None

    # --- L5 Disk-backed Cold Cache ---
    def demote_to_l5(self, key: str, compressed_bytes: bytes):
        filepath = os.path.join(self.cold_cache_dir, f"{key}.bin")
        try:
            with open(filepath, "wb") as f:
                f.write(compressed_bytes)
            self.l5_disk_keys[key] = filepath
        except Exception:
            pass

    def get_l5(self, key: str) -> Optional[Any]:
        if key in self.l5_disk_keys and os.path.exists(self.l5_disk_keys[key]):
            try:
                with open(self.l5_disk_keys[key], "rb") as f:
                    compressed = f.read()
                raw = zlib.decompress(compressed)
                return pickle.loads(raw)
            except Exception:
                return None
        return None

    def get_stats(self) -> Dict[str, int]:
        return {
            "l1_active_allocated": int(self.l1_active_frame is not None),
            "l2_history_count": len(self.l2_history_frames),
            "l3_scene_entries": len(self.l3_scene_cache),
            "l4_compressed_entries": len(self.l4_compressed_states),
            "l5_cold_disk_entries": len(self.l5_disk_keys),
        }
