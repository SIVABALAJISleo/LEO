"""
cbe/scheduling/variable_rate.py
Variable Rate Shading (VRS) simulator and shading rate map generator.
Maps perceptual importance and motion into DirectX 12 VRS Tier 1/2 compatible rate maps
(1x1, 2x1, 1x2, 2x2, 4x4) with software tile coarsening fallback.
"""

from __future__ import annotations

import enum
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any


class ShadingRate(enum.IntEnum):
    RATE_1X1 = 0   # 1 sample per pixel (100% shading cost)
    RATE_2X1 = 1   # 1 sample per 2x1 pixels (50% shading cost)
    RATE_1X2 = 2   # 1 sample per 1x2 pixels (50% shading cost)
    RATE_2X2 = 3   # 1 sample per 2x2 pixels (25% shading cost)
    RATE_4X4 = 4   # 1 sample per 4x4 pixels (6.25% shading cost)


class VariableRateShading:
    """
    Computes screen-space shading rate allocations.
    High-contrast / high-importance tiles run at 1x1, while flat / motion-blurred / background
    tiles execute at 2x2 or 4x4, eliminating up to 75% of pixel fragment invocations.
    """
    RATE_INVOCATION_COST = {
        ShadingRate.RATE_1X1: 1.000,
        ShadingRate.RATE_2X1: 0.500,
        ShadingRate.RATE_1X2: 0.500,
        ShadingRate.RATE_2X2: 0.250,
        ShadingRate.RATE_4X4: 0.0625,
    }

    def __init__(
        self,
        tile_size: int = 16,
        high_importance_thresh: float = 0.70,
        medium_importance_thresh: float = 0.40,
        hardware_vrs_supported: bool = False
    ):
        self.tile_size = tile_size
        self.high_thresh = high_importance_thresh
        self.med_thresh = medium_importance_thresh
        self.hardware_vrs_supported = hardware_vrs_supported

    def generate_rate_map(self, importance_map: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Generates tile-level shading rate matrix.
        Returns: (rate_map, shading_invocation_reduction_pct).
        """
        H, W = importance_map.shape
        tiles_y = (H + self.tile_size - 1) // self.tile_size
        tiles_x = (W + self.tile_size - 1) // self.tile_size
        
        rate_map = np.zeros((tiles_y, tiles_x), dtype=np.uint8)
        total_cost = 0.0
        
        for ty in range(tiles_y):
            y_start = ty * self.tile_size
            y_end = min(H, y_start + self.tile_size)
            for tx in range(tiles_x):
                x_start = tx * self.tile_size
                x_end = min(W, x_start + self.tile_size)
                
                mean_imp = float(np.mean(importance_map[y_start:y_end, x_start:x_end]))
                
                if mean_imp >= self.high_thresh:
                    rate = ShadingRate.RATE_1X1
                elif mean_imp >= self.med_thresh:
                    rate = ShadingRate.RATE_2X2
                else:
                    rate = ShadingRate.RATE_4X4
                    
                rate_map[ty, tx] = int(rate)
                total_cost += self.RATE_INVOCATION_COST[rate]
                
        baseline_cost = float(tiles_y * tiles_x)
        reduction_pct = (1.0 - (total_cost / max(1.0, baseline_cost))) * 100.0
        return rate_map, reduction_pct

    def apply_software_vrs(self, frame: np.ndarray, rate_map: np.ndarray) -> np.ndarray:
        """
        Software fallback: coarsens pixel sampling in tiles marked 2x2 or 4x4.
        """
        H, W, C = frame.shape
        coarsened = frame.copy()
        tiles_y, tiles_x = rate_map.shape
        
        for ty in range(tiles_y):
            y_start = ty * self.tile_size
            y_end = min(H, y_start + self.tile_size)
            for tx in range(tiles_x):
                x_start = tx * self.tile_size
                x_end = min(W, x_start + self.tile_size)
                
                rate = ShadingRate(rate_map[ty, tx])
                block = coarsened[y_start:y_end, x_start:x_end]
                
                if rate == ShadingRate.RATE_2X2:
                    # 2x2 average downsampling
                    step = 2
                    for y in range(0, block.shape[0], step):
                        for x in range(0, block.shape[1], step):
                            avg = np.mean(block[y:y+step, x:x+step], axis=(0, 1))
                            block[y:y+step, x:x+step] = avg
                elif rate == ShadingRate.RATE_4X4:
                    # 4x4 average downsampling
                    step = 4
                    for y in range(0, block.shape[0], step):
                        for x in range(0, block.shape[1], step):
                            avg = np.mean(block[y:y+step, x:x+step], axis=(0, 1))
                            block[y:y+step, x:x+step] = avg
                            
        return coarsened
