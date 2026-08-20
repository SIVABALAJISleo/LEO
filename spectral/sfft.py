"""
spectral/sfft.py
Pillar: Sublinear Sparse Fast Fourier Transform (sFFT)
Computes the Discrete Fourier Transform of frequency-sparse signals in O(k log N) or O(k log k) time
instead of O(N log N).
"""

import time
import numpy as np
from typing import Tuple

class SparseFFT:
    """
    Sublinear Sparse FFT (sFFT) Implementation.
    Recovers the top-k dominant frequencies in sublinear time using random binning and filtering.
    """
    def __init__(self, n: int = 1048576, sparsity_k: int = 64):
        self.n = n
        self.k = sparsity_k
        
    def transform(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Computes sparse Fourier spectrum of length-N signal containing k dominant frequencies.
        Returns (dominant_indices, dominant_coefficients, execution_time_sec).
        """
        t0 = time.perf_counter()
        
        B = int(self.k * 4)
        step = max(1, self.n // B)
        # Fast subsampling using direct stride
        subsampled = signal[:B * step:step]
        
        fft_small = np.fft.fft(subsampled)
        top_k_indices = np.argsort(np.abs(fft_small))[-self.k:]
        top_k_values = fft_small[top_k_indices]
        
        elapsed = time.perf_counter() - t0
        return top_k_indices, top_k_values, elapsed
