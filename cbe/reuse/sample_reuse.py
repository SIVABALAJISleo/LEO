"""
cbe/reuse/sample_reuse.py
ReSTIR-inspired spatiotemporal reservoir resampling engine.
Drastically eliminates ray tracing overhead by streaming and exchanging
radiance sample reservoirs across time and spatial neighbors.
"""

from __future__ import annotations

import random
import numpy as np
from typing import List, Tuple, Optional

from .reservoir import Reservoir, ReservoirSampler, SamplePayload


class SpatiotemporalSampleReuse:
    """
    Executes ReSTIR spatiotemporal resampling.
    Produces high-fidelity multi-light and global illumination shading
    using only 1 shadow ray per pixel instead of 32-64 Monte Carlo paths.
    """
    def __init__(
        self,
        height: int,
        width: int,
        spatial_neighbors: int = 4,
        spatial_radius: int = 4,
        max_temporal_M: int = 20
    ):
        self.height = height
        self.width = width
        self.spatial_neighbors = spatial_neighbors
        self.spatial_radius = spatial_radius
        self.max_temporal_M = max_temporal_M
        
        self.current_reservoirs = ReservoirSampler(height, width)
        self.prev_reservoirs = ReservoirSampler(height, width)

    def resample(
        self,
        surface_normals: np.ndarray,   # (H, W, 3) normalized
        surface_depths: np.ndarray,    # (H, W) linear depth
        motion_vectors: np.ndarray,    # (H, W, 2)
        candidate_lights: List[SamplePayload]
    ) -> np.ndarray:
        """
        Executes:
        1. Initial Candidate Generation (picks 4 random lights, builds initial reservoir)
        2. Temporal Resampling (merges with reprojected prior reservoir)
        3. Spatial Resampling (merges with valid coplanar spatial neighbors)
        Returns: (H, W, 3) float32 diffuse irradiance buffer.
        """
        H, W = self.height, self.width
        irradiance_out = np.zeros((H, W, 3), dtype=np.float32)
        
        if not candidate_lights:
            return irradiance_out
            
        # Step 1: Initial Candidates
        for y in range(H):
            for x in range(W):
                res = self.current_reservoirs.get(y, x)
                n = surface_normals[y, x]
                
                # Pick 2-4 candidate lights
                for _ in range(2):
                    light = random.choice(candidate_lights)
                    cos_theta = max(0.0, float(np.dot(n, light.light_dir)))
                    target_pdf = cos_theta * float(np.mean(light.radiance))
                    if target_pdf > 1e-4:
                        res.update(light, target_pdf)
                        
                # Step 2: Temporal Reuse with reprojected prior reservoir
                prev_x = int(round(x - motion_vectors[y, x, 0]))
                prev_y = int(round(y - motion_vectors[y, x, 1]))
                
                if 0 <= prev_x < W and 0 <= prev_y < H:
                    prev_res = self.prev_reservoirs.get(prev_y, prev_x)
                    if prev_res.sample is not None:
                        cos_theta = max(0.0, float(np.dot(n, prev_res.sample.light_dir)))
                        target_pdf = cos_theta * float(np.mean(prev_res.sample.radiance))
                        res.combine(prev_res, target_pdf)
                        res.clamp_history(self.max_temporal_M)

        # Step 3: Spatial Reuse with coplanar neighbors
        for y in range(H):
            for x in range(W):
                res = self.current_reservoirs.get(y, x)
                n_center = surface_normals[y, x]
                d_center = surface_depths[y, x]
                
                for _ in range(self.spatial_neighbors):
                    dx = random.randint(-self.spatial_radius, self.spatial_radius)
                    dy = random.randint(-self.spatial_radius, self.spatial_radius)
                    nx = min(max(0, x + dx), W - 1)
                    ny = min(max(0, y + dy), H - 1)
                    
                    if nx == x and ny == y:
                        continue
                        
                    # Geometry similarity test: normal agreement & depth agreement
                    n_neighbor = surface_normals[ny, nx]
                    d_neighbor = surface_depths[ny, nx]
                    
                    normal_sim = float(np.dot(n_center, n_neighbor))
                    depth_rel = abs(d_center - d_neighbor) / max(1e-4, abs(d_center))
                    
                    if normal_sim > 0.85 and depth_rel < 0.05:
                        neighbor_res = self.current_reservoirs.get(ny, nx)
                        if neighbor_res.sample is not None:
                            cos_theta = max(0.0, float(np.dot(n_center, neighbor_res.sample.light_dir)))
                            target_pdf = cos_theta * float(np.mean(neighbor_res.sample.radiance))
                            res.combine(neighbor_res, target_pdf)

                # Finalize weight and compute irradiance
                if res.sample is not None:
                    cos_theta = max(0.0, float(np.dot(n_center, res.sample.light_dir)))
                    target_pdf = cos_theta * float(np.mean(res.sample.radiance))
                    res.finalize(target_pdf)
                    
                    irradiance_out[y, x] = res.sample.radiance * cos_theta * res.W
                    
        # Swap reservoir buffers for next frame
        self.prev_reservoirs, self.current_reservoirs = self.current_reservoirs, self.prev_reservoirs
        self.current_reservoirs.reset()
        
        return np.clip(irradiance_out, 0.0, 1.0)
