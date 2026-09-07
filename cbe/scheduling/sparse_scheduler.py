"""
cbe/scheduling/sparse_scheduler.py
Batches sparse tiles into coalesced rectangular dispatches.
Minimizes kernel launch overhead and maximizes Intel GPU execution unit occupancy.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class CoalescedRegion:
    min_x: int
    min_y: int
    width: int
    height: int
    tile_count: int


class SparseTileScheduler:
    """
    Coalesces scattered sparse tiles into contiguous bounding boxes
    to prevent fine-grained launch thrashing on the GPU command queue.
    """
    def __init__(self, tile_size: int = 16, merge_proximity_px: int = 32):
        self.tile_size = tile_size
        self.merge_proximity = merge_proximity_px

    def coalesce_tiles(
        self,
        active_tiles: List[Tuple[int, int, int, int]],
        viewport_w: int,
        viewport_h: int
    ) -> List[CoalescedRegion]:
        """
        active_tiles: list of (x, y, w, h).
        Returns coalesced bounding boxes.
        """
        if not active_tiles:
            return []
            
        regions: List[CoalescedRegion] = []
        for x, y, w, h in active_tiles:
            merged = False
            for r in regions:
                # Check bounding box proximity
                if (abs(x - r.min_x) <= self.merge_proximity + r.width and
                    abs(y - r.min_y) <= self.merge_proximity + r.height):
                    # Expand region
                    new_min_x = min(r.min_x, x)
                    new_min_y = min(r.min_y, y)
                    new_max_x = max(r.min_x + r.width, x + w)
                    new_max_y = max(r.min_y + r.height, y + h)
                    
                    r.min_x = new_min_x
                    r.min_y = new_min_y
                    r.width = min(viewport_w - new_min_x, new_max_x - new_min_x)
                    r.height = min(viewport_h - new_min_y, new_max_y - new_min_y)
                    r.tile_count += 1
                    merged = True
                    break
                    
            if not merged:
                regions.append(CoalescedRegion(
                    min_x=x,
                    min_y=y,
                    width=w,
                    height=h,
                    tile_count=1
                ))
                
        return regions
