"""
cbe/residual/residual_classifier.py
Classifies spatial tiles into 9 formal compute strategies:
UNCHANGED, REPROJECTABLE, PREDICTABLE, CACHEABLE, INTERPOLATABLE,
RECONSTRUCTABLE, APPROXIMABLE, NOVEL, UNKNOWN.
"""

from __future__ import annotations

import enum
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


class ResidualClass(enum.Enum):
    UNCHANGED = "UNCHANGED"              # Zero compute: exact historical pixel reuse
    REPROJECTABLE = "REPROJECTABLE"      # Subpixel motion warp from history
    PREDICTABLE = "PREDICTABLE"          # Kinematic / Kalman future frame extrapolation
    CACHEABLE = "CACHEABLE"              # Direct semantic/radiance cache hit
    INTERPOLATABLE = "INTERPOLATABLE"    # Spatiotemporal neighbor blend
    RECONSTRUCTABLE = "RECONSTRUCTABLE"  # Low-res rendering + neural reconstruction
    APPROXIMABLE = "APPROXIMABLE"        # Low-precision / coarse VRS pass
    NOVEL = "NOVEL"                      # Fresh high-fidelity compute strictly required
    UNKNOWN = "UNKNOWN"                  # Safe fallback to standard computation


@dataclass
class TileClassification:
    tile_x: int
    tile_y: int
    tile_w: int
    tile_h: int
    residual_class: ResidualClass
    mean_residual: float
    confidence: float
    disoccluded_fraction: float


class ResidualClassifier:
    """
    Partitions the image into discrete tiles (e.g., 16x16 pixels)
    and categorizes each tile into its optimal compute strategy.
    """
    def __init__(
        self,
        tile_size: int = 16,
        unchanged_thresh: float = 0.02,
        reprojectable_thresh: float = 0.08,
        approximable_thresh: float = 0.20,
        confidence_thresh: float = 0.80
    ):
        self.tile_size = tile_size
        self.unchanged_thresh = unchanged_thresh
        self.reprojectable_thresh = reprojectable_thresh
        self.approximable_thresh = approximable_thresh
        self.confidence_thresh = confidence_thresh

    def classify_tiles(
        self,
        residual_map: np.ndarray,
        confidence_map: np.ndarray,
        disocclusion_mask: np.ndarray,
        cache_hit_mask: Optional[np.ndarray] = None
    ) -> List[TileClassification]:
        """
        Classifies all grid tiles across the viewport.
        """
        H, W = residual_map.shape
        tiles: List[TileClassification] = []
        
        for y in range(0, H, self.tile_size):
            h_actual = min(self.tile_size, H - y)
            for x in range(0, W, self.tile_size):
                w_actual = min(self.tile_size, W - x)
                
                tile_res = residual_map[y:y+h_actual, x:x+w_actual]
                tile_conf = confidence_map[y:y+h_actual, x:x+w_actual]
                tile_disocc = disocclusion_mask[y:y+h_actual, x:x+w_actual]
                
                mean_res = float(np.mean(tile_res))
                mean_conf = float(np.mean(tile_conf))
                disocc_frac = float(np.sum(tile_disocc)) / float(tile_disocc.size)
                
                has_cache_hit = False
                if cache_hit_mask is not None:
                    has_cache_hit = bool(np.mean(cache_hit_mask[y:y+h_actual, x:x+w_actual]) > 0.9)

                # Classification Rules
                if disocc_frac > 0.30:
                    r_class = ResidualClass.NOVEL
                elif mean_res < self.unchanged_thresh and mean_conf >= self.confidence_thresh:
                    r_class = ResidualClass.UNCHANGED
                elif has_cache_hit:
                    r_class = ResidualClass.CACHEABLE
                elif mean_conf >= self.confidence_thresh and mean_res < self.reprojectable_thresh:
                    r_class = ResidualClass.REPROJECTABLE
                elif mean_conf >= 0.60 and mean_res < self.approximable_thresh:
                    r_class = ResidualClass.RECONSTRUCTABLE
                elif mean_res < self.approximable_thresh:
                    r_class = ResidualClass.APPROXIMABLE
                else:
                    r_class = ResidualClass.NOVEL
                    
                tiles.append(TileClassification(
                    tile_x=x,
                    tile_y=y,
                    tile_w=w_actual,
                    tile_h=h_actual,
                    residual_class=r_class,
                    mean_residual=mean_res,
                    confidence=mean_conf,
                    disoccluded_fraction=disocc_frac
                ))
                
        return tiles
