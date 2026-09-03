"""
hyper_mvc_dar/adaptive.py
Adaptive Computation Engine: Dynamically scales computation effort
(sampling rates, resolution tiers, iteration counts) according to workload difficulty.
"""

from typing import Dict, Any, Tuple
import numpy as np


class AdaptiveComputeEngine:
    """Dynamically scales sampling and resolution tiers."""

    @staticmethod
    def evaluate_adaptive_sampling(
        current_samples: int,
        sample_variance: float,
        target_error: float
    ) -> Tuple[bool, int]:
        """
        Determines whether Monte Carlo sampling has converged or more samples are needed.
        Standard Error = sqrt(Variance / N)
        """
        if current_samples == 0:
            return False, 1000

        standard_error = np.sqrt(max(1e-12, sample_variance) / current_samples)
        if standard_error <= target_error:
            return True, 0  # Converged

        # Estimate required remaining samples: N_needed = Variance / (target_error^2)
        needed_total = int(sample_variance / (target_error ** 2))
        additional_needed = max(100, needed_total - current_samples)
        return False, additional_needed

    @staticmethod
    def select_resolution_scale(target_fps: float, current_frame_time_ms: float) -> float:
        """Dynamically scales rendering resolution between 0.5 (540p) and 1.0 (1080p)."""
        target_frame_time_ms = 1000.0 / max(1.0, target_fps)
        if current_frame_time_ms <= target_frame_time_ms * 0.8:
            return 1.0  # Full native resolution
        elif current_frame_time_ms <= target_frame_time_ms * 1.2:
            return 0.75  # 720p reconstruction
        else:
            return 0.50  # 540p aggressive downscale
