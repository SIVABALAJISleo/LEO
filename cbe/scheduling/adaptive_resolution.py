"""
cbe/scheduling/adaptive_resolution.py
Dynamic resolution scaling controller.
Dynamically adjusts render scale (33% to 100%) to lock frame rates without visible blur,
leveraging temporal & neural reconstruction to restore native presentation targets.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any


@dataclass
class ResolutionTier:
    scale: float
    name: str
    relative_fillrate: float  # scale^2


class AdaptiveResolutionController:
    """
    Hysteresis-stabilized dynamic resolution governor.
    Evaluates GPU/CPU frametimes, thermal state, and motion to select optimal internal render scale.
    """
    AVAILABLE_TIERS: List[ResolutionTier] = [
        ResolutionTier(scale=1.00, name="NATIVE_100", relative_fillrate=1.000),
        ResolutionTier(scale=0.90, name="ULTRA_QUALITY_90", relative_fillrate=0.810),
        ResolutionTier(scale=0.80, name="QUALITY_80", relative_fillrate=0.640),
        ResolutionTier(scale=0.75, name="BALANCED_HIGH_75", relative_fillrate=0.562),
        ResolutionTier(scale=0.67, name="BALANCED_67", relative_fillrate=0.449),
        ResolutionTier(scale=0.60, name="PERFORMANCE_60", relative_fillrate=0.360),
        ResolutionTier(scale=0.50, name="ULTRA_PERF_50", relative_fillrate=0.250),
        ResolutionTier(scale=0.33, name="EXTREME_BYPASS_33", relative_fillrate=0.109),
    ]

    def __init__(
        self,
        target_fps: float = 60.0,
        min_scale: float = 0.33,
        max_scale: float = 1.00,
        hysteresis_frames: int = 5
    ):
        self.target_fps = target_fps
        self.target_frametime_ms = 1000.0 / target_fps
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.hysteresis_frames = hysteresis_frames
        
        # Start at balanced (0.75)
        self.current_tier_idx = 3
        self._stable_frame_count = 0
        self.resolution_history: List[float] = []

    def get_current_scale(self) -> float:
        return self.AVAILABLE_TIERS[self.current_tier_idx].scale

    def compute_internal_dimensions(self, target_width: int, target_height: int) -> Tuple[int, int]:
        scale = self.get_current_scale()
        # Ensure dimensions are multiples of 2 (or 16 for tile alignment)
        w = max(32, int(round((target_width * scale) / 2.0)) * 2)
        h = max(32, int(round((target_height * scale) / 2.0)) * 2)
        return w, h

    def update(
        self,
        frame_time_ms: float,
        gpu_load: float = 0.8,
        thermal_throttling: bool = False,
        reconstruction_confidence: float = 0.90,
        motion_magnitude: float = 0.0
    ) -> float:
        """
        Updates controller state and returns recommended render scale.
        """
        time_ratio = frame_time_ms / max(1.0, self.target_frametime_ms)
        
        # Emergency downgrade conditions:
        # 1. Frame time exceeds budget by > 20%
        # 2. Thermal throttling active
        # 3. GPU load pegged at 100%
        should_downgrade = (time_ratio > 1.20) or thermal_throttling or (gpu_load > 0.95 and time_ratio > 1.05)
        
        # Upgrade conditions:
        # 1. Frame time comfortably under budget (< 80%)
        # 2. High reconstruction confidence
        # 3. No thermal throttling
        should_upgrade = (time_ratio < 0.80) and (reconstruction_confidence >= 0.85) and not thermal_throttling
        
        # Motion modulation: during intense fast motion, downscaling is less perceptible
        if motion_magnitude > 20.0 and should_downgrade:
            self._stable_frame_count += 2
        elif should_downgrade:
            self._stable_frame_count += 1
        elif should_upgrade:
            self._stable_frame_count -= 1
        else:
            self._stable_frame_count = 0

        # Apply state transition with hysteresis
        if self._stable_frame_count >= self.hysteresis_frames:
            # Downgrade: increment tier index (lower scale)
            if self.current_tier_idx < len(self.AVAILABLE_TIERS) - 1:
                tier = self.AVAILABLE_TIERS[self.current_tier_idx + 1]
                if tier.scale >= self.min_scale:
                    self.current_tier_idx += 1
            self._stable_frame_count = 0
            
        elif self._stable_frame_count <= -self.hysteresis_frames:
            # Upgrade: decrement tier index (higher scale)
            if self.current_tier_idx > 0:
                tier = self.AVAILABLE_TIERS[self.current_tier_idx - 1]
                if tier.scale <= self.max_scale:
                    self.current_tier_idx -= 1
            self._stable_frame_count = 0

        current_scale = self.get_current_scale()
        self.resolution_history.append(current_scale)
        return current_scale
