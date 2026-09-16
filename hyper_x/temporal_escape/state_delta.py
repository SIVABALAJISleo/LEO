#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/temporal_escape/state_delta.py
======================================
Phase 9: State Delta and Incremental Compute.
Calculates state differences between consecutive frames/simulation steps:
  Δ(t) = S(t) - S(t-1)
Identifies dirty spatial masks, applies local neighborhood bounding envelopes
to prevent historical smear/ghosting, and applies updates incrementally.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import numpy as np


@dataclass
class StateDeltaResult:
    delta_tensor: np.ndarray
    dirty_mask: np.ndarray
    dirty_fraction: float
    is_mostly_static: bool
    requires_full_refresh: bool


class StateDeltaEngine:
    """
    Computes sparse state differences across time steps.
    """

    def __init__(self, dirty_threshold: float = 1e-4, fallback_threshold: float = 0.75):
        self.dirty_threshold = dirty_threshold
        self.fallback_threshold = fallback_threshold

    def compute_delta(
        self,
        prev_state: np.ndarray,
        curr_state: np.ndarray,
    ) -> StateDeltaResult:
        if prev_state.shape != curr_state.shape:
            raise ValueError(f"Shape mismatch: {prev_state.shape} vs {curr_state.shape}")

        diff = curr_state - prev_state
        dirty_mask = np.abs(diff) > self.dirty_threshold
        dirty_fraction = float(np.sum(dirty_mask) / max(curr_state.size, 1))

        # If dirty fraction exceeds fallback threshold (e.g. 75%), fallback to full evaluation
        requires_full = dirty_fraction >= self.fallback_threshold

        return StateDeltaResult(
            delta_tensor=diff,
            dirty_mask=dirty_mask,
            dirty_fraction=dirty_fraction,
            is_mostly_static=dirty_fraction < 0.20,
            requires_full_refresh=requires_full,
        )

    def apply_neighborhood_clamping(
        self,
        history_state: np.ndarray,
        curr_state: np.ndarray,
        kernel_size: int = 3,
    ) -> np.ndarray:
        """
        Anti-ghosting color/state bounding box clamping.
        Clamps historical values to [min, max] of current local spatial neighborhood.
        """
        if history_state.ndim < 2:
            return np.clip(history_state, np.min(curr_state), np.max(curr_state))

        # Neighborhood min/max approximation using slicing
        min_box = curr_state.copy()
        max_box = curr_state.copy()

        # 3x3 box filter min/max
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                rolled = np.roll(np.roll(curr_state, dy, axis=0), dx, axis=1)
                min_box = np.minimum(min_box, rolled)
                max_box = np.maximum(max_box, rolled)

        return np.clip(history_state, min_box, max_box)
