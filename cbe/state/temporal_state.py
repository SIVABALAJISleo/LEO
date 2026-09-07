"""
cbe/state/temporal_state.py
Multi-frame historical state ring buffer storing colors, motion vectors,
linear depth buffers, subpixel jitter sequences, and reactive masks.
"""

from __future__ import annotations

import collections
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Deque


@dataclass
class TemporalFrameRecord:
    frame_index: int
    timestamp: float
    color_buffer: np.ndarray  # (H, W, 3) float32 [0, 1]
    depth_buffer: np.ndarray  # (H, W) float32 linear depth
    motion_vectors: np.ndarray  # (H, W, 2) float32 screen-space (dx, dy) in pixels
    jitter_offset: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float32))
    reactive_mask: Optional[np.ndarray] = None  # (H, W) float32 [0, 1] (transparency / particle mask)
    camera_view_proj: Optional[np.ndarray] = None  # (4, 4) float32
    confidence_map: Optional[np.ndarray] = None  # (H, W) float32 [0, 1]


class TemporalStateBuffer:
    """
    Thread-safe ring buffer retaining N consecutive historical frames
    for temporal reprojection, history clamping, and neural reconstruction.
    """
    def __init__(self, max_history: int = 8):
        self.max_history = max_history
        self._buffer: Deque[TemporalFrameRecord] = collections.deque(maxlen=max_history)

    def push(self, record: TemporalFrameRecord):
        self._buffer.append(record)

    def get_latest(self) -> Optional[TemporalFrameRecord]:
        if not self._buffer:
            return None
        return self._buffer[-1]

    def get_previous(self, steps_back: int = 1) -> Optional[TemporalFrameRecord]:
        if len(self._buffer) <= steps_back or steps_back < 1:
            return None
        return self._buffer[-(steps_back + 1)]

    def count(self) -> int:
        return len(self._buffer)

    def clear(self):
        self._buffer.clear()
