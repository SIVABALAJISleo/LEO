#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/graphics/display.py
===========================
Total GPU Omega: Display Pipeline & Frame Pacer.

Responsibilities:
  - Swapchain buffering & presentation synchronization
  - Adaptive frame pacing
  - Latency and jitter measurement
  - Dropped frame tracking
"""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
import numpy as np


class DisplayPipeline:
    """
    Software display pipeline managing presentation timing, buffer flips,
    and frame latency jitter on host displays.
    """

    def __init__(self, target_fps: float = 60.0, num_buffers: int = 2):
        self.target_fps = target_fps
        self.target_frame_time_ms = 1000.0 / target_fps
        self.num_buffers = num_buffers
        self.frame_history_ms: List[float] = []
        self.last_present_time: float = 0.0
        self.total_frames_presented: int = 0
        self.dropped_frames: int = 0

    def present_frame(self, frame_buffer: np.ndarray) -> Dict[str, Any]:
        """Simulates swapchain flip, pacing, and records frame-to-frame delta."""
        now = time.perf_counter()
        if self.last_present_time > 0.0:
            frame_delta_ms = (now - self.last_present_time) * 1000.0
            self.frame_history_ms.append(frame_delta_ms)
            if len(self.frame_history_ms) > 120:
                self.frame_history_ms.pop(0)

            # Check if frame missed target deadline
            if frame_delta_ms > self.target_frame_time_ms * 1.5:
                self.dropped_frames += 1
        else:
            frame_delta_ms = self.target_frame_time_ms

        self.last_present_time = now
        self.total_frames_presented += 1

        # Calculate pacing jitter: standard deviation of frame times
        jitter = float(np.std(self.frame_history_ms)) if len(self.frame_history_ms) > 1 else 0.0

        return {
            "frame_index": self.total_frames_presented,
            "target_fps": self.target_fps,
            "frame_delta_ms": round(frame_delta_ms, 3),
            "pacing_jitter_ms": round(jitter, 3),
            "dropped_frames": self.dropped_frames,
            "swapchain_depth": self.num_buffers
        }
