"""
cbe/reuse/reservoir.py
Mathematical Weighted Reservoir Sampling (WRS) for ReSTIR spatiotemporal sample reuse.
Implements candidate selection, streaming accumulation, and unbiased weight normalization.
"""

from __future__ import annotations

import random
import numpy as np
from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass
class SamplePayload:
    light_dir: np.ndarray      # (3,) float32 direction to light
    radiance: np.ndarray       # (3,) float32 incoming radiance (RGB)
    distance: float            # distance to light source
    light_id: int              # discrete light index


class Reservoir:
    """
    Mathematical ReSTIR Reservoir structure tracking streaming candidate samples.
    """
    def __init__(self):
        self.sample: Optional[SamplePayload] = None
        self.w_sum: float = 0.0   # Sum of candidate weights
        self.M: int = 0           # Number of samples considered
        self.W: float = 0.0       # Final Monte Carlo estimator weight

    def update(self, candidate: SamplePayload, weight: float) -> bool:
        """Streaming update: selects candidate with probability weight / (w_sum + weight)."""
        self.w_sum += weight
        self.M += 1
        
        # Selection probability: weight / w_sum
        if self.w_sum > 0 and random.random() < (weight / self.w_sum):
            self.sample = candidate
            return True
        return False

    def combine(self, other: Reservoir, target_pdf: float):
        """Combines another reservoir into this one (temporal or spatial reuse)."""
        if other.M <= 0 or other.sample is None:
            return
            
        weight = target_pdf * other.W * other.M
        if self.update(other.sample, weight):
            pass
        self.M += (other.M - 1)  # update() already added 1 to M

    def finalize(self, target_pdf: float):
        """Calculates final unbiased normalization weight W."""
        if self.M > 0 and target_pdf > 1e-7 and self.w_sum > 0:
            self.W = self.w_sum / (self.M * target_pdf)
        else:
            self.W = 0.0

    def clamp_history(self, max_M: int = 20):
        """Clamps M to prevent temporal lag when dynamic lights move."""
        if self.M > max_M:
            scale = float(max_M) / float(self.M)
            self.w_sum *= scale
            self.M = max_M


class ReservoirSampler:
    """Manages 2D grids of reservoirs for screen-space resampling."""
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.grid: List[List[Reservoir]] = [
            [Reservoir() for _ in range(width)] for _ in range(height)
        ]

    def get(self, y: int, x: int) -> Reservoir:
        return self.grid[y][x]

    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = Reservoir()
