"""
cbe/residual/residual_renderer.py
Executes sparse rendering exclusively on scheduled residual tiles
and composites them seamlessly with the predicted/reprojected base.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Callable, Dict, Any, Optional

from .residual_scheduler import SparseWorkSchedule


class ResidualRenderer:
    """
    Renders only necessary novel or high-residual regions,
    compositing them with the predicted frame to assemble the final output.
    """
    def __init__(self, blend_edges: bool = True):
        self.blend_edges = blend_edges

    def render_residual_frame(
        self,
        predicted_frame: np.ndarray,
        schedule: SparseWorkSchedule,
        tile_render_fn: Callable[[int, int, int, int, float], np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Renders scheduled tiles and stitches the final frame.
        tile_render_fn signature: (x, y, w, h, fidelity_scale) -> (h, w, 3) float32
        """
        t0 = time.perf_counter()
        output = predicted_frame.copy()
        tiles_computed = 0
        
        # 1. Render fresh high-fidelity tiles (NOVEL)
        for t in schedule.fresh_tiles:
            rendered = tile_render_fn(t.tile_x, t.tile_y, t.tile_w, t.tile_h, 1.0)
            output[t.tile_y:t.tile_y+t.tile_h, t.tile_x:t.tile_x+t.tile_w] = rendered
            tiles_computed += 1
            
        # 2. Render coarse/approximated tiles (APPROXIMABLE)
        for t in schedule.approximated_tiles:
            # Render at half resolution (0.5 scale) and interpolate
            rendered = tile_render_fn(t.tile_x, t.tile_y, t.tile_w, t.tile_h, 0.5)
            output[t.tile_y:t.tile_y+t.tile_h, t.tile_x:t.tile_x+t.tile_w] = rendered
            tiles_computed += 1
            
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        
        return np.clip(output, 0.0, 1.0), {
            "elapsed_ms": elapsed_ms,
            "total_tiles": schedule.total_tiles,
            "computed_tiles": tiles_computed,
            "reused_tiles": len(schedule.reused_tiles),
            "tiles_saved_pct": round((1.0 - (tiles_computed / max(1, schedule.total_tiles))) * 100.0, 2),
            "measured_cer": schedule.compute_elimination_ratio,
        }
