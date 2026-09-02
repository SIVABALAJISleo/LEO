"""
hyper_v2/analysis/redundancy_analyzer.py
Analyzes temporal, spatial, and mathematical redundancy in tensor data and compute streams.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class RedundancyAnalyzer:
    """Detects temporal, spatial, and algebraic redundancy in compute workloads."""

    @staticmethod
    def compute_temporal_coherence(frame_prev: np.ndarray, frame_curr: np.ndarray, tolerance: float = 1e-2) -> float:
        """Returns the ratio of pixels/elements that haven't changed beyond tolerance."""
        if frame_prev.shape != frame_curr.shape:
            return 0.0
        diff = np.abs(frame_curr - frame_prev)
        unchanged = np.sum(diff <= tolerance)
        return float(unchanged / max(1, frame_curr.size))

    @staticmethod
    def detect_eigenspectrum_decay(matrix: np.ndarray, energy_threshold: float = 0.95) -> Dict[str, Any]:
        """Analyzes singular value decay to determine if low-rank truncation is viable."""
        if matrix.ndim != 2:
            return {"is_low_rank": False, "effective_rank": min(matrix.shape), "energy_ratio": 1.0}

        try:
            # Approximate top 32 singular values
            k = min(32, min(matrix.shape))
            U, S, Vt = np.linalg.svd(matrix[:128, :128], full_matrices=False)
            total_energy = np.sum(S ** 2)
            cum_energy = np.cumsum(S ** 2) / max(1e-12, total_energy)
            rank_k = int(np.searchsorted(cum_energy, energy_threshold) + 1)
            is_low_rank = rank_k <= (k // 2)
            return {
                "is_low_rank": is_low_rank,
                "effective_rank": rank_k,
                "decay_rate": float((S[0] - S[-1]) / max(1e-12, S[0])),
                "cumulative_energy_retained": float(cum_energy[min(len(cum_energy)-1, rank_k-1)])
            }
        except Exception:
            return {"is_low_rank": False, "effective_rank": min(matrix.shape), "energy_ratio": 1.0}
