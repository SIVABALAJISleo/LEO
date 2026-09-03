"""
hyper_v3/intelligence/sparsity.py
Analyzes structured, unstructured, 2:4 block, and frequency-domain sparsity.
"""

from typing import Dict, Any, Tuple
import numpy as np


class SparsityAnalyzer:
    """Characterizes sparsity patterns in tensors."""

    @staticmethod
    def measure_unstructured_sparsity(tensor: np.ndarray, threshold: float = 1e-6) -> float:
        total = tensor.size
        if total == 0:
            return 0.0
        zeros = np.count_nonzero(np.abs(tensor) <= threshold)
        return float(zeros / total)

    @staticmethod
    def check_2_to_4_sparsity(matrix: np.ndarray, threshold: float = 1e-6) -> Tuple[bool, float]:
        if matrix.ndim != 2 or matrix.shape[1] % 4 != 0:
            return False, 0.0
        reshaped = matrix.reshape(matrix.shape[0], -1, 4)
        zero_mask = np.abs(reshaped) <= threshold
        zero_counts = np.sum(zero_mask, axis=2)
        valid_blocks = np.sum(zero_counts >= 2)
        total_blocks = zero_counts.size
        compliance_ratio = float(valid_blocks / total_blocks) if total_blocks > 0 else 0.0
        return bool(compliance_ratio >= 0.95), compliance_ratio

    @staticmethod
    def analyze_frequency_sparsity(signal: np.ndarray, top_energy_threshold: float = 0.99) -> Dict[str, Any]:
        if signal.size < 4:
            return {"spectral_sparsity": 0.0, "dominant_frequencies": signal.size}
        fft_coeffs = np.abs(np.fft.rfft(signal))
        total_energy = np.sum(fft_coeffs**2)
        if total_energy == 0:
            return {"spectral_sparsity": 1.0, "dominant_frequencies": 0}
        sorted_energy = np.sort(fft_coeffs**2)[::-1]
        cumulative = np.cumsum(sorted_energy) / total_energy
        idx = np.searchsorted(cumulative, top_energy_threshold) + 1
        return {
            "spectral_sparsity": float(1.0 - (idx / len(fft_coeffs))),
            "dominant_frequencies": int(idx),
            "total_frequencies": len(fft_coeffs)
        }
