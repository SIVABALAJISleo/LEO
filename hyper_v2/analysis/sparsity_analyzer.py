"""
hyper_v2/analysis/sparsity_analyzer.py
Measures structured, unstructured, 2:4 block, and frequency-domain sparsity.
"""

from typing import Dict, Any, Tuple
import numpy as np


class SparsityAnalyzer:
    """Detects and characterizes sparsity patterns across tensor representations."""

    @staticmethod
    def analyze_sparsity(tensor: np.ndarray, zero_threshold: float = 1e-6) -> Dict[str, Any]:
        total_elements = tensor.size
        if total_elements == 0:
            return {"sparsity_ratio": 0.0, "is_sparse": False, "is_2_4_structured": False}

        zero_count = int(np.sum(np.abs(tensor) <= zero_threshold))
        sparsity_ratio = zero_count / total_elements

        # Check 2:4 structured sparsity (2 zeros out of every 4 elements along last dimension)
        is_2_4 = False
        if tensor.ndim >= 2 and tensor.shape[-1] % 4 == 0:
            reshaped = np.abs(tensor).reshape(-1, 4)
            zeros_per_4 = np.sum(reshaped <= zero_threshold, axis=1)
            is_2_4 = bool(np.mean(zeros_per_4 >= 2) > 0.90)

        return {
            "total_elements": total_elements,
            "zero_elements": zero_count,
            "sparsity_ratio": float(sparsity_ratio),
            "sparsity_pct": float(sparsity_ratio * 100.0),
            "is_sparse": sparsity_ratio > 0.50,
            "is_highly_sparse": sparsity_ratio > 0.85,
            "is_2_4_structured": is_2_4,
            "recommended_sparse_format": "CSR" if sparsity_ratio > 0.8 else ("2:4_SIMD" if is_2_4 else "DENSE")
        }

    @staticmethod
    def analyze_frequency_sparsity(signal: np.ndarray, energy_threshold: float = 0.98) -> Dict[str, Any]:
        """Estimates dominant spectral peaks in 1D/2D signal."""
        try:
            fft_vals = np.abs(np.fft.fft(signal.flatten()))
            sorted_indices = np.argsort(fft_vals)[::-1]
            cum_energy = np.cumsum(fft_vals[sorted_indices] ** 2)
            total_energy = cum_energy[-1] + 1e-12
            k_peaks = int(np.searchsorted(cum_energy / total_energy, energy_threshold) + 1)

            return {
                "signal_length": len(signal.flatten()),
                "k_dominant_peaks": k_peaks,
                "sparsity_factor": float(1.0 - (k_peaks / len(signal.flatten()))),
                "is_frequency_sparse": k_peaks <= (len(signal.flatten()) // 8)
            }
        except Exception:
            return {"k_dominant_peaks": len(signal.flatten()), "is_frequency_sparse": False}
