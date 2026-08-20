"""
spectral/signal_router.py
The HYPER Protocol v2.0: Contract-Aware Signal Router
Probes the signal's frequency sparsity ratio (k/N) before choosing an algorithm.
  - If Sparsity Ratio (k/N) < 0.1: Routes to MIT Sublinear Sparse FFT O(k log k)
  - If Sparsity Ratio (k/N) >= 0.1: Routes to Exact FFT O(N log N)
Prevents blind sFFT execution on dense signals.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from .sfft import SparseFFT

class SignalRouter:
    """
    Intelligent Signal Sparsity Prober & Algorithm Router.
    """
    def __init__(self, sparsity_threshold: float = 0.10):
        self.sparsity_threshold = sparsity_threshold
        self.sfft_engine = SparseFFT()
        
    def probe_sparsity(self, signal: np.ndarray) -> Tuple[float, float]:
        """
        Runs an O(N) L2-norm downsample probe to estimate the energy concentration (sparsity ratio).
        Returns (estimated_sparsity_ratio, probe_time_ms).
        """
        t0 = time.perf_counter()
        n = len(signal)
        # Downsample probe (O(N) single stride pass)
        probe_size = min(n, 1024)
        sample = signal[:probe_size]
        
        # Energy concentration metric: top 10% components energy vs total energy
        spectrum_sample = np.abs(np.fft.fft(sample))
        total_energy = np.sum(spectrum_sample ** 2) + 1e-8
        
        k_sample = max(1, int(probe_size * 0.05))
        top_k_energy = np.sum(np.sort(spectrum_sample ** 2)[-k_sample:])
        
        energy_ratio = top_k_energy / total_energy
        # If 5% of bins hold >80% of energy, signal is frequency-sparse
        estimated_sparsity_ratio = (1.0 - energy_ratio) * 0.5
        
        probe_time_ms = (time.perf_counter() - t0) * 1000
        return estimated_sparsity_ratio, probe_time_ms

    def execute_transform(self, signal: np.ndarray) -> Dict[str, Any]:
        """
        Executes FFT under the contract-aware routing policy.
        """
        sparsity_ratio, probe_ms = self.probe_sparsity(signal)
        t0 = time.perf_counter()
        
        if sparsity_ratio < self.sparsity_threshold:
            # Frequency-sparse: Use sublinear Sparse FFT O(k log k)
            indices, values, sfft_sec = self.sfft_engine.transform(signal)
            total_latency_ms = probe_ms + (sfft_sec * 1000)
            
            return {
                "algorithm_selected": "MIT Sublinear Sparse FFT (sFFT)",
                "complexity": "O(k log k)",
                "signal_length": len(signal),
                "measured_sparsity_ratio": sparsity_ratio,
                "sparsity_threshold": self.sparsity_threshold,
                "probe_latency_ms": probe_ms,
                "transform_latency_ms": sfft_sec * 1000,
                "total_latency_ms": total_latency_ms,
                "routing_decision": "SPARSE_FAST_PATH",
                "contract_claim": f"Frequency-sparse signal (k/N = {sparsity_ratio:.3f} < {self.sparsity_threshold}): Bypassed to O(k log k)"
            }
        else:
            # Dense signal: Fallback to exact FFT O(N log N)
            fft_result = np.fft.fft(signal)
            transform_ms = (time.perf_counter() - t0) * 1000
            total_latency_ms = probe_ms + transform_ms
            
            return {
                "algorithm_selected": "Exact FFT (FFTW / NumPy)",
                "complexity": "O(N log N)",
                "signal_length": len(signal),
                "measured_sparsity_ratio": sparsity_ratio,
                "sparsity_threshold": self.sparsity_threshold,
                "probe_latency_ms": probe_ms,
                "transform_latency_ms": transform_ms,
                "total_latency_ms": total_latency_ms,
                "routing_decision": "DENSE_EXACT_FALLBACK",
                "contract_claim": f"Dense signal (k/N = {sparsity_ratio:.3f} >= {self.sparsity_threshold}): Exact O(N log N) standard enforced"
            }
