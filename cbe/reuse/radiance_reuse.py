"""
cbe/reuse/radiance_reuse.py
Spatial hash-grid radiance cache.
Caches incoming and outgoing radiance samples indexed by 3D world position and surface normal.
Bypasses ray casting whenever a valid radiance estimate already exists.
"""

from __future__ import annotations

import hashlib
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any


@dataclass
class RadianceEntry:
    radiance: np.ndarray       # (3,) float32
    sample_count: int
    last_frame_accessed: int
    confidence: float


class RadianceCache:
    """
    World-space hash-grid radiance cache.
    Maps (quantized 3D position, normal) to incoming indirect radiance.
    """
    def __init__(self, cell_size: float = 0.10, max_entries: int = 100000):
        self.cell_size = cell_size
        self.max_entries = max_entries
        self.cache: Dict[Tuple[int, int, int, int, int, int], RadianceEntry] = {}
        self.current_frame = 0
        self.hit_count = 0
        self.miss_count = 0

    def _hash_key(self, pos: np.ndarray, normal: np.ndarray) -> Tuple[int, int, int, int, int, int]:
        # Quantize world position to cell grid
        gx = int(np.floor(pos[0] / self.cell_size))
        gy = int(np.floor(pos[1] / self.cell_size))
        gz = int(np.floor(pos[2] / self.cell_size))
        
        # Quantize normal vector into discrete bins
        nx = int(np.clip(np.round(normal[0] * 4.0), -4, 4))
        ny = int(np.clip(np.round(normal[1] * 4.0), -4, 4))
        nz = int(np.clip(np.round(normal[2] * 4.0), -4, 4))
        
        return (gx, gy, gz, nx, ny, nz)

    def query(self, pos: np.ndarray, normal: np.ndarray) -> Tuple[Optional[np.ndarray], bool, float]:
        """
        Attempts cache lookup.
        Returns: (radiance, hit_found, confidence).
        """
        key = self._hash_key(pos, normal)
        entry = self.cache.get(key)
        
        if entry is not None:
            # Decay confidence based on age
            age = self.current_frame - entry.last_frame_accessed
            conf = max(0.0, entry.confidence * (0.95 ** age))
            if conf >= 0.50:
                self.hit_count += 1
                entry.last_frame_accessed = self.current_frame
                return entry.radiance, True, conf
                
        self.miss_count += 1
        return None, False, 0.0

    def store(self, pos: np.ndarray, normal: np.ndarray, radiance: np.ndarray):
        """Stores or merges a computed radiance sample."""
        if len(self.cache) >= self.max_entries:
            self._purge_stale()
            
        key = self._hash_key(pos, normal)
        entry = self.cache.get(key)
        
        if entry is None:
            self.cache[key] = RadianceEntry(
                radiance=radiance.astype(np.float32),
                sample_count=1,
                last_frame_accessed=self.current_frame,
                confidence=1.0
            )
        else:
            # Exponential moving average blending
            alpha = 1.0 / float(min(16, entry.sample_count + 1))
            entry.radiance = (1.0 - alpha) * entry.radiance + alpha * radiance
            entry.sample_count += 1
            entry.last_frame_accessed = self.current_frame
            entry.confidence = min(1.0, entry.confidence + 0.1)

    def step_frame(self):
        self.current_frame += 1

    def _purge_stale(self):
        stale_keys = [
            k for k, v in self.cache.items()
            if (self.current_frame - v.last_frame_accessed) > 10
        ]
        for k in stale_keys:
            del self.cache[k]

    def get_stats(self) -> Dict[str, Any]:
        total = self.hit_count + self.miss_count
        return {
            "cached_cells": len(self.cache),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_ratio_pct": round((self.hit_count / max(1, total)) * 100.0, 2),
        }
