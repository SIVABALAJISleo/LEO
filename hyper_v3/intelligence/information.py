"""
hyper_v3/intelligence/information.py
Measures information density, Shannon entropy, gradient sensitivity, and spatial/temporal variance.
"""

from typing import Dict, Any
import numpy as np


class InformationAnalyzer:
    """Computes information density, entropy, and sensitivity."""

    @staticmethod
    def compute_shannon_entropy(tensor: np.ndarray, bins: int = 64) -> float:
        flat = tensor.ravel()
        if flat.size < 2:
            return 0.0
        hist, _ = np.histogram(flat, bins=bins, density=True)
        hist = hist[hist > 0]
        entropy = -float(np.sum(hist * np.log2(hist + 1e-12)))
        return max(0.0, entropy)

    @staticmethod
    def compute_variance_density(tensor: np.ndarray) -> float:
        flat = tensor.ravel()
        if flat.size < 2:
            return 0.0
        var = float(np.var(flat))
        mean_abs = float(np.mean(np.abs(flat))) + 1e-12
        return float(var / (mean_abs**2))

    @staticmethod
    def estimate_gradient_sensitivity(input_matrix: np.ndarray, weight_matrix: np.ndarray) -> Dict[str, Any]:
        """Estimates output sensitivity to input perturbations."""
        if input_matrix.ndim == 2 and weight_matrix.ndim == 2:
            # Norm of weights bounds the Lipschitz constant
            fro_norm = float(np.linalg.norm(weight_matrix, 'fro'))
            spectral_norm = float(np.linalg.norm(weight_matrix, 2))
            return {
                "frobenius_norm": fro_norm,
                "spectral_norm": spectral_norm,
                "lipschitz_bound": spectral_norm
            }
        return {"lipschitz_bound": 1.0}
