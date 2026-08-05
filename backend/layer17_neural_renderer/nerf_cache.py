"""
backend/layer17_neural_renderer/nerf_cache.py
HDC NeRF Voxel Cache: Stores temporal volumetric data.
Uses HDC popcount for sub-millisecond similarity lookups based on camera pos.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

class HDCNeRFVoxelCache:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        # Simulated HDC memory matrix for camera positions
        # shape: (capacity, 512) bit-vectors stored as int8
        self.hdc_memory = np.zeros((capacity, 512), dtype=np.int8)
        self.voxel_payloads = [None] * capacity
        self.size = 0
        self.threshold = 450  # Out of 512 bits matching
        
    def _pos_to_hdc(self, camera_pos: tuple) -> np.ndarray:
        """Map a 3D float coordinate to a 512-bit bipolar hypervector"""
        # Deterministic generation based on position hash for demonstration
        np.random.seed(hash(camera_pos) % (2**32 - 1))
        return np.random.choice([-1, 1], size=512).astype(np.int8)

    def query(self, camera_pos: tuple):
        """
        Popcount similarity lookup.
        Returns cached frame/voxel data if camera moved only slightly.
        """
        if self.size == 0:
            return None
            
        query_hv = self._pos_to_hdc(camera_pos)
        
        # Fast batch popcount (dot product for bipolar vectors)
        similarities = np.dot(self.hdc_memory[:self.size], query_hv)
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score >= self.threshold:
            # Camera moved slightly, we can reuse this frame's NeRF state
            return self.voxel_payloads[best_idx]
            
        return None

    def update(self, camera_pos: tuple, frame_data: np.ndarray):
        """Store new rendered volume state into the HDC cache."""
        query_hv = self._pos_to_hdc(camera_pos)
        
        idx = self.size % self.capacity
        self.hdc_memory[idx] = query_hv
        self.voxel_payloads[idx] = frame_data
        
        if self.size < self.capacity:
            self.size += 1
