"""
hyper_v3/intelligence/redundancy.py
Temporal, spatial, and mathematical redundancy discovery engine.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class RedundancyAnalyzer:
    """Discovers temporal coherence, spatial smoothness, and eigenspectrum decay."""

    @staticmethod
    def measure_temporal_coherence(prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        if prev_frame.shape != curr_frame.shape:
            return 0.0
        diff = np.abs(curr_frame - prev_frame)
        max_val = max(float(np.max(np.abs(curr_frame))), 1e-6)
        normalized_diff = float(np.mean(diff) / max_val)
        return float(max(0.0, 1.0 - normalized_diff))

    @staticmethod
    def measure_spatial_smoothness(matrix: np.ndarray) -> float:
        if matrix.ndim != 2:
            return 0.0
        grad_x = np.abs(np.diff(matrix, axis=1))
        grad_y = np.abs(np.diff(matrix, axis=0))
        mean_grad = float(np.mean(grad_x) + np.mean(grad_y))
        scale = max(float(np.std(matrix)), 1e-6)
        smoothness = 1.0 / (1.0 + (mean_grad / scale))
        return float(smoothness)

    @staticmethod
    def compute_eigenspectrum_decay(matrix: np.ndarray, top_k: int = 10) -> Dict[str, Any]:
        if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 2:
            return {"energy_ratio_top_k": 1.0, "decay_rate": 0.0}
        try:
            u, s, vh = np.linalg.svd(matrix, full_matrices=False)
            total_energy = float(np.sum(s**2))
            top_energy = float(np.sum(s[:top_k]**2)) if total_energy > 0 else 0.0
            ratio = top_energy / total_energy if total_energy > 0 else 1.0
            return {
                "energy_ratio_top_k": float(ratio),
                "singular_values_top": [float(x) for x in s[:top_k]],
                "decay_rate": float(s[0] / max(s[-1], 1e-12))
            }
        except Exception:
            return {"energy_ratio_top_k": 1.0, "decay_rate": 0.0}
