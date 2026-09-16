"""
hyper/importance/importance_engine.py
=====================================
HYPER Importance Engine & Region-Based Allocation:
Evaluates spatial and object importance in [0.0, 1.0].
Implements:
- HyperImportanceEngine (configurable semantic & perceptual policies)
- RegionScheduler (spatial compute effort allocation)
- ImportanceScheduler
- ResolutionAllocator (variable-rate shading & resolution scaling per region)
- ComputeBudgetAllocator (allocating millisecond frame budget across tiles)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class ImportancePolicy:
    """Configurable weights for importance factors."""
    category_weights: Dict[str, float] = field(default_factory=lambda: {
        "player": 1.00,
        "weapon": 1.00,
        "enemy": 0.95,
        "interactive": 0.90,
        "geometry": 0.75,
        "midground": 0.55,
        "background": 0.35,
        "sky": 0.20,
    })
    distance_falloff_power: float = 0.5
    motion_boost_weight: float = 0.25
    center_focal_weight: float = 0.20
    min_importance_floor: float = 0.15


class HyperImportanceEngine:
    """
    Computes spatial importance map and individual object importance scores.
    """

    def __init__(self, policy: Optional[ImportancePolicy] = None):
        self.policy = policy or ImportancePolicy()

    def evaluate_object_importance(
        self,
        category: str,
        distance: float,
        screen_size_fraction: float,
        velocity_magnitude: float = 0.0,
        is_focused: bool = False,
    ) -> float:
        """
        Computes composite importance score in [0.0, 1.0].
        """
        base_cat = self.policy.category_weights.get(category, 0.5)
        
        # Distance attenuation
        dist_factor = 1.0 / (1.0 + (max(0.0, distance) ** self.policy.distance_falloff_power) * 0.05)
        
        # Screen coverage bonus
        size_bonus = min(0.3, screen_size_fraction * 0.5)
        
        # Motion importance (moving threats/objects draw human attention)
        motion_bonus = min(0.2, velocity_magnitude * self.policy.motion_boost_weight)
        
        # Focus bonus (crosshair / camera center focus)
        focus_bonus = self.policy.center_focal_weight if is_focused else 0.0

        importance = (base_cat * dist_factor) + size_bonus + motion_bonus + focus_bonus
        return float(np.clip(importance, self.policy.min_importance_floor, 1.0))

    def generate_spatial_importance_map(
        self,
        grid_shape: Tuple[int, int] = (60, 80),
        focal_point_norm: Tuple[float, float] = (0.5, 0.5),
        object_quadrants: Optional[List[Tuple[float, float, float, float]]] = None,
    ) -> np.ndarray:
        """
        Generates a 2D importance map normalized to [0.0, 1.0].
        """
        h, w = grid_shape
        y_coords, x_coords = np.mgrid[0:h, 0:w]
        norm_y = y_coords / max(1, h - 1)
        norm_x = x_coords / max(1, w - 1)

        # Center gaze / crosshair focal weight
        fx, fy = focal_point_norm
        dist_to_focus = np.sqrt((norm_x - fx) ** 2 + (norm_y - fy) ** 2)
        focal_map = np.clip(1.0 - dist_to_focus * 1.2, 0.2, 1.0) * self.policy.center_focal_weight

        importance_map = np.full((h, w), self.policy.min_importance_floor, dtype=np.float32) + focal_map

        # Splat object quadrants if provided: (x_min, y_min, x_max, y_max, score)
        if object_quadrants:
            for x0, y0, x1, y1, score in object_quadrants:
                ix0 = max(0, int(x0 * w))
                ix1 = min(w, int(x1 * w))
                iy0 = max(0, int(y0 * h))
                iy1 = min(h, int(y1 * h))
                importance_map[iy0:iy1, ix0:ix1] = np.maximum(importance_map[iy0:iy1, ix0:ix1], score)

        return np.clip(importance_map, 0.0, 1.0)


class ResolutionAllocator:
    """
    Maps spatial importance to variable internal rendering resolutions.
    Regions with low importance (background, peripheral vision) are computed at lower resolution
    and reconstructed to output resolution, radically eliminating shading cost.
    """

    TIER_100_PCT = 1.0   # Full resolution 1:1 shading
    TIER_75_PCT  = 0.75  # 75% resolution
    TIER_50_PCT  = 0.50  # Half resolution (4x reduction in pixel shading)
    TIER_25_PCT  = 0.25  # Quarter resolution (16x reduction)

    @classmethod
    def allocate_region_scale(cls, importance_score: float) -> float:
        if importance_score >= 0.85:
            return cls.TIER_100_PCT
        elif importance_score >= 0.60:
            return cls.TIER_75_PCT
        elif importance_score >= 0.35:
            return cls.TIER_50_PCT
        else:
            return cls.TIER_25_PCT


class ComputeBudgetAllocator:
    """
    Enforces a strict frame budget deadline (e.g. 16.6 ms for 60 FPS) across regions.
    """

    def __init__(self, target_frame_budget_ms: float = 16.6):
        self.target_budget_ms = target_frame_budget_ms

    def partition_budget(
        self, importance_map: np.ndarray, num_tiles_x: int = 4, num_tiles_y: int = 4
    ) -> np.ndarray:
        """
        Partitions the frame millisecond budget across a tile grid proportional to mean tile importance.
        """
        h, w = importance_map.shape
        tile_h = h // num_tiles_y
        tile_w = w // num_tiles_x

        tile_importances = np.zeros((num_tiles_y, num_tiles_x), dtype=np.float32)
        for ty in range(num_tiles_y):
            for tx in range(num_tiles_x):
                sub = importance_map[ty*tile_h:(ty+1)*tile_h, tx*tile_w:(tx+1)*tile_w]
                tile_importances[ty, tx] = float(np.mean(sub))

        total_imp = float(np.sum(tile_importances))
        if total_imp <= 1e-5:
            return np.full((num_tiles_y, num_tiles_x), self.target_budget_ms / (num_tiles_x * num_tiles_y))

        budget_distribution = (tile_importances / total_imp) * self.target_budget_ms
        return budget_distribution


class RegionScheduler:
    """
    Coordinates spatial tile execution:
    Selects whether a region should be:
    - 100% Exact Shaded
    - Reconstructed via Motion Vectors
    - Partially Shaded at Reduced Resolution
    - Copied from Temporal Cache
    """

    def __init__(self, target_fps: int = 60):
        self.target_budget_ms = 1000.0 / target_fps
        self.importance_engine = HyperImportanceEngine()
        self.budget_allocator = ComputeBudgetAllocator(self.target_budget_ms)

    def schedule_tiles(
        self,
        importance_map: np.ndarray,
        uncertainty_map: np.ndarray,
        can_reuse_map: np.ndarray,
        num_tiles: Tuple[int, int] = (4, 4),
    ) -> List[Dict[str, Any]]:
        """
        Produces an actionable scheduling plan for each tile.
        """
        ty_count, tx_count = num_tiles
        h, w = importance_map.shape
        th = h // ty_count
        tw = w // tx_count

        tiles_plan = []
        for ty in range(ty_count):
            for tx in range(tx_count):
                y0, y1 = ty * th, (ty + 1) * th
                x0, x1 = tx * tw, (tx + 1) * tw

                tile_imp = float(np.mean(importance_map[y0:y1, x0:x1]))
                tile_unc = float(np.mean(uncertainty_map[y0:y1, x0:x1]))
                tile_can_reuse = bool(np.mean(can_reuse_map[y0:y1, x0:x1]) > 0.8)

                if tile_can_reuse and tile_unc < 0.2:
                    action = "TEMPORAL_REUSE"
                    scale = 0.0  # Zero computation
                elif tile_unc > 0.7 or tile_imp > 0.9:
                    action = "FULL_COMPUTE"
                    scale = 1.0
                elif tile_unc > 0.35 or tile_imp > 0.5:
                    action = "PARTIAL_RECONSTRUCT"
                    scale = ResolutionAllocator.allocate_region_scale(tile_imp)
                else:
                    action = "REPROJECT_RECONSTRUCT"
                    scale = 0.25

                tiles_plan.append({
                    "tile_id": f"T_{ty}_{tx}",
                    "bounds": (x0, y0, x1, y1),
                    "mean_importance": round(tile_imp, 3),
                    "mean_uncertainty": round(tile_unc, 3),
                    "action": action,
                    "resolution_scale": scale,
                })

        return tiles_plan
