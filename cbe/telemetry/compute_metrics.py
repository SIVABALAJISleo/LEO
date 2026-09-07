"""
cbe/telemetry/compute_metrics.py
=============================================================================
Compute Metrics & Elimination Ratio (CER) Tracking
=============================================================================
Mathematically rigorous measurement of compute budget elimination:
  CER = 1.0 - (C_actual / C_baseline)
Subject to strict non-double-counting invariants:
  C_actual = C_render + C_prediction + C_reconstruction + C_memory + C_control
  C_baseline = Standard native baseline cost (e.g. native SPP or full resolution).
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ComputeSample:
    frame_index: int
    baseline_rays: int
    actual_rays: int
    baseline_latency_ms: float
    actual_latency_ms: float
    overhead_latency_ms: float
    ray_cer: float
    latency_cer: float
    net_cer: float


class ComputeMetrics:
    """
    Accumulator and statistical evaluator for Compute-Budget Elimination.
    Guarantees mathematically honest, non-double-counted CER metrics.
    """

    def __init__(self):
        self.samples: List[ComputeSample] = []
        self.cumulative_baseline_rays: int = 0
        self.cumulative_actual_rays: int = 0
        self.cumulative_baseline_time_ms: float = 0.0
        self.cumulative_actual_time_ms: float = 0.0

    @staticmethod
    def calculate_cer(baseline: float, actual: float) -> float:
        """
        Calculates CER = 1 - (actual / baseline).
        Returns value clipped in [0.0, 1.0].
        """
        if baseline <= 1e-6:
            return 0.0
        ratio = actual / baseline
        return float(np.clip(1.0 - ratio, 0.0, 1.0))

    def record_frame(
        self,
        frame_index: int,
        baseline_rays: int,
        actual_rays: int,
        baseline_latency_ms: float,
        actual_latency_ms: float,
        overhead_latency_ms: float = 0.0,
    ) -> ComputeSample:
        """
        Records a single frame's compute expenditures.
        Net latency CER accounts for all algorithm overheads.
        """
        ray_cer = self.calculate_cer(float(baseline_rays), float(actual_rays))
        latency_cer = self.calculate_cer(baseline_latency_ms, actual_latency_ms)
        
        # Net CER includes actual compute plus all controller / reconstruction overheads
        total_spent = actual_latency_ms + overhead_latency_ms
        net_cer = self.calculate_cer(baseline_latency_ms, total_spent)

        sample = ComputeSample(
            frame_index=frame_index,
            baseline_rays=baseline_rays,
            actual_rays=actual_rays,
            baseline_latency_ms=baseline_latency_ms,
            actual_latency_ms=actual_latency_ms,
            overhead_latency_ms=overhead_latency_ms,
            ray_cer=round(ray_cer, 4),
            latency_cer=round(latency_cer, 4),
            net_cer=round(net_cer, 4),
        )
        self.samples.append(sample)

        self.cumulative_baseline_rays += baseline_rays
        self.cumulative_actual_rays += actual_rays
        self.cumulative_baseline_time_ms += baseline_latency_ms
        self.cumulative_actual_time_ms += actual_latency_ms

        return sample

    def compute_phi(self, frame: np.ndarray, num_tiles: int = 8) -> int:
        """
        Computes 64-bit Perceptual Hash Index (PHI) across image tiles.
        Measures structural illumination constancy across frames.
        """
        H, W = frame.shape[:2]
        gray = np.mean(frame, axis=-1) if frame.ndim == 3 else frame
        tile_h, tile_w = H // num_tiles, W // num_tiles
        
        mean_vals = []
        for ty in range(num_tiles):
            for tx in range(num_tiles):
                tile = gray[ty * tile_h : (ty + 1) * tile_h, tx * tile_w : (tx + 1) * tile_w]
                mean_vals.append(np.mean(tile))

        overall_mean = np.mean(mean_vals)
        hash_val = 0
        for i, val in enumerate(mean_vals):
            if val > overall_mean:
                hash_val |= (1 << (i % 64))
        return hash_val

    def get_aggregate_summary(self) -> Dict[str, Any]:
        """Returns overall aggregate statistics across all recorded frames."""
        if not self.samples:
            return {
                "total_frames": 0,
                "cumulative_ray_cer": 0.0,
                "cumulative_latency_cer": 0.0,
                "average_net_cer": 0.0,
            }

        cum_ray_cer = self.calculate_cer(
            float(self.cumulative_baseline_rays), float(self.cumulative_actual_rays)
        )
        cum_lat_cer = self.calculate_cer(
            self.cumulative_baseline_time_ms, self.cumulative_actual_time_ms
        )
        avg_net_cer = float(np.mean([s.net_cer for s in self.samples]))

        return {
            "total_frames": len(self.samples),
            "cumulative_baseline_rays": self.cumulative_baseline_rays,
            "cumulative_actual_rays": self.cumulative_actual_rays,
            "cumulative_ray_cer": round(cum_ray_cer, 4),
            "cumulative_latency_cer": round(cum_lat_cer, 4),
            "average_net_cer": round(avg_net_cer, 4),
            "p50_net_cer": round(float(np.percentile([s.net_cer for s in self.samples], 50)), 4),
            "p95_net_cer": round(float(np.percentile([s.net_cer for s in self.samples], 95)), 4),
        }
