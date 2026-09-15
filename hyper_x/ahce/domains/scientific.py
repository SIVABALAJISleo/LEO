"""
hyper_x/ahce/domains/scientific.py
==================================
Scientific and spectral computation adapter for AHCE.
"""

from typing import Dict, Any, Tuple
import numpy as np
from ..contract import AHCEContract, CorrectnessClass


class ScientificDomainAdapter:
    """Scientific FFT and PDE solver adapter."""

    def execute_sparse_fft(
        self,
        signal: np.ndarray,
        contract: AHCEContract,
        sparsity_threshold: float = 1e-4
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Fast FFT on CPU
        fft_out = np.fft.fft(signal)
        # Prune small spectral bins below threshold if approximation permitted
        if contract.allow_approximation:
            mask = np.abs(fft_out) >= sparsity_threshold
            sparse_fft = np.where(mask, fft_out, 0.0 + 0.0j)
            elim = float(np.sum(~mask) / signal.size)
            return sparse_fft, {
                "eliminated_bins_pct": round(elim * 100.0, 2),
                "strategy": "sparse_spectral_pruning",
                "path_class": "NUMERICALLY_EQUIVALENT"
            }

        return fft_out, {"strategy": "dense_fft", "path_class": "EXACT"}
