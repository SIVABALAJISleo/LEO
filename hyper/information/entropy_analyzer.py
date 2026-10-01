"""
hyper/information/entropy_analyzer.py
=====================================
Information-Theoretic Analysis Layer for LEO/HYPER.
Fulfills Section 36 of the Breakthrough Master Architecture.

Estimates:
- Input Shannon Entropy (bits/symbol)
- Output Shannon Entropy
- Theoretical Compressibility
- Redundancy Ratio
- Temporal Redundancy (Frame-to-Frame mutual variation)
- Spatial Redundancy (Local smoothness / total variation)
- Optimization Guidance Recommendation

CRITICAL SCIENTIFIC PRINCIPLE:
Do NOT use entropy estimates as proof of computational lower bounds.
Use them exclusively to guide optimization search and algorithm selection.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class InformationProfile:
    """Quantitative information-theoretic profile of a workload tensor."""
    def __init__(
        self,
        shannon_entropy_bits: float,
        max_possible_entropy_bits: float,
        compressibility_ratio: float,
        redundancy_ratio: float,
        spatial_redundancy: Optional[float] = None,
        temporal_redundancy: Optional[float] = None,
        optimization_recommendation: str = "EXACT_STANDARD_SEARCH",
    ):
        self.shannon_entropy_bits = shannon_entropy_bits
        self.max_possible_entropy_bits = max_possible_entropy_bits
        self.compressibility_ratio = compressibility_ratio
        self.redundancy_ratio = redundancy_ratio
        self.spatial_redundancy = spatial_redundancy
        self.temporal_redundancy = temporal_redundancy
        self.optimization_recommendation = optimization_recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shannon_entropy_bits": round(self.shannon_entropy_bits, 4),
            "max_possible_entropy_bits": round(self.max_possible_entropy_bits, 4),
            "compressibility_ratio": round(self.compressibility_ratio, 4),
            "redundancy_ratio": round(self.redundancy_ratio, 4),
            "spatial_redundancy": round(self.spatial_redundancy, 4) if self.spatial_redundancy is not None else None,
            "temporal_redundancy": round(self.temporal_redundancy, 4) if self.temporal_redundancy is not None else None,
            "optimization_recommendation": self.optimization_recommendation,
            "methodology_disclaimer": "Entropy estimates guide optimization search only, NOT mathematical lower bounds.",
        }


class InformationTheoreticAnalyzer:
    """
    Analyzes input and output tensors to guide escape compiler search strategy.
    """

    @staticmethod
    def compute_shannon_entropy(tensor: np.ndarray, num_bins: int = 256) -> Tuple[float, float]:
        """
        Computes discrete Shannon entropy: H(X) = -sum(p_i * log2(p_i)).
        Returns (actual_entropy_bits, max_entropy_bits).
        """
        if tensor.size == 0:
            return 0.0, 0.0

        # Discretize continuous data into histogram bins
        flat = tensor.flatten()
        hist, _ = np.histogram(flat, bins=min(num_bins, max(2, len(np.unique(flat)))))
        probs = hist / float(tensor.size)
        probs = probs[probs > 0]  # Exclude zero probabilities

        entropy = float(-np.sum(probs * np.log2(probs)))
        max_entropy = float(np.log2(num_bins))

        return entropy, max_entropy

    @staticmethod
    def compute_spatial_smoothness(matrix: np.ndarray) -> float:
        """
        Computes normalized total variation as a measure of spatial redundancy.
        Lower variation -> Higher spatial redundancy (smooth images/fields).
        """
        if matrix.ndim < 2 or matrix.shape[0] < 2 or matrix.shape[1] < 2:
            return 0.0

        diff_h = np.abs(matrix[1:, :] - matrix[:-1, :])
        diff_v = np.abs(matrix[:, 1:] - matrix[:, :-1])
        tv = float(np.mean(diff_h) + np.mean(diff_v))
        std = float(np.std(matrix)) + 1e-12
        normalized_tv = tv / std
        # Spatial redundancy = 1.0 - normalized_tv clipped
        return float(max(0.0, min(1.0, 1.0 - (normalized_tv / 2.0))))

    @staticmethod
    def compute_temporal_correlation(curr: np.ndarray, prev: np.ndarray) -> float:
        """
        Computes temporal redundancy between consecutive frames.
        Returns correlation coefficient in [0.0, 1.0].
        """
        if curr.shape != prev.shape or curr.size == 0:
            return 0.0

        f_curr = curr.flatten()
        f_prev = prev.flatten()
        std_c = np.std(f_curr)
        std_p = np.std(f_prev)
        if std_c < 1e-9 or std_p < 1e-9:
            return 1.0 if np.array_equal(f_curr, f_prev) else 0.0

        corr = np.corrcoef(f_curr, f_prev)[0, 1]
        return float(max(0.0, min(1.0, corr))) if not np.isnan(corr) else 0.0

    def analyze(
        self,
        tensor: np.ndarray,
        prev_frame: Optional[np.ndarray] = None,
    ) -> InformationProfile:
        """
        Builds complete Information Profile to guide search strategy.
        """
        entropy, max_entropy = self.compute_shannon_entropy(tensor)
        redundancy = max(0.0, 1.0 - (entropy / max(1e-6, max_entropy)))
        compressibility = 1.0 / max(0.01, (entropy / max(1e-6, max_entropy)))

        spatial_red = None
        if tensor.ndim >= 2:
            spatial_red = self.compute_spatial_smoothness(tensor)

        temporal_red = None
        if prev_frame is not None and prev_frame.shape == tensor.shape:
            temporal_red = self.compute_temporal_correlation(tensor, prev_frame)

        # Optimization Recommendation
        zero_fraction = float(np.mean(tensor == 0))
        if zero_fraction > 0.6:
            rec = "RECOMMEND_SPARSE_REPRESENTATION"
        elif temporal_red is not None and temporal_red > 0.85:
            rec = "RECOMMEND_TEMPORAL_DELTA_INCREMENTAL"
        elif spatial_red is not None and spatial_red > 0.80:
            rec = "RECOMMEND_SEPARABLE_OR_FREQUENCY_DECOMPOSITION"
        elif redundancy < 0.10:
            rec = "RECOMMEND_EXACT_FALLBACK_HIGH_ENTROPY"
        else:
            rec = "RECOMMEND_STANDARD_ALGEBRAIC_SEARCH"

        return InformationProfile(
            shannon_entropy_bits=entropy,
            max_possible_entropy_bits=max_entropy,
            compressibility_ratio=compressibility,
            redundancy_ratio=redundancy,
            spatial_redundancy=spatial_red,
            temporal_redundancy=temporal_red,
            optimization_recommendation=rec,
        )
