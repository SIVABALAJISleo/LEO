"""
hyper/escape_engine/workloads/convolution_2d.py
===============================================
VAEE Initial Research Workload: 2D Image Convolution.

Compares:
- Direct 2D spatial convolution: O(H * W * Kh * Kw)
- Separable rank-1 filter decomposition: O(H * W * (Kh + Kw))
- Verifies numerical equivalence
"""

from __future__ import annotations

import numpy as np
from scipy import signal
from typing import Any, Dict

from ..contracts.schema import ComputationalContract
from ..verification.verifier import MasterVerifier
from ..analysis.cost_model import CostAnalyzer


class Convolution2DResearchWorkload:
    """Workload evaluating separable filter decomposition for 2D convolution."""

    def __init__(self, H: int = 256, W: int = 256, K: int = 15, seed: int = 42) -> None:
        self.H, self.W, self.K = H, W, K
        self.rng = np.random.default_rng(seed)
        self.image = self.rng.standard_normal((H, W)).astype(np.float32)

        # 1D Gaussian kernel
        x = np.linspace(-3, 3, K)
        k1d = np.exp(-0.5 * x ** 2).astype(np.float32)
        k1d /= np.sum(k1d)
        self.k1d = k1d
        # Outer product produces rank-1 2D kernel
        self.kernel2d = np.outer(k1d, k1d).astype(np.float32)

        # Ground truth: direct 2D convolution
        self.ref_out = signal.convolve2d(self.image, self.kernel2d, mode="same", boundary="symm")

        self.contract = ComputationalContract(
            contract_id=f"conv2d_{H}x{W}_k{K}",
            input_type="matrix",
            output_type="matrix",
            input_shape=(H, W),
            output_shape=(H, W),
            correctness="NUMERICAL",
            numeric_tolerance=1e-4,
            verification_method="EXACT_DIFFERENTIAL",
        )

    def direct_conv(self) -> np.ndarray:
        return signal.convolve2d(self.image, self.kernel2d, mode="same", boundary="symm")

    def separable_conv(self) -> np.ndarray:
        """Separable 2D convolution via two consecutive 1D passes."""
        # Row pass
        row_pass = signal.convolve2d(self.image, self.k1d[None, :], mode="same", boundary="symm")
        # Column pass
        return signal.convolve2d(row_pass, self.k1d[:, None], mode="same", boundary="symm")

    def run_benchmark(self) -> Dict[str, Any]:
        _, direct_cost = CostAnalyzer.measure_execution(self.direct_conv, trials=3)
        _, sep_cost = CostAnalyzer.measure_execution(self.separable_conv, trials=5)

        res = self.separable_conv()
        verifier = MasterVerifier()
        v_res = verifier.verify_candidate(res, self.ref_out, self.contract)

        speedup = direct_cost.wall_clock_ms / max(1e-6, sep_cost.wall_clock_ms)

        return {
            "workload": f"Conv2D_{self.H}x{self.W}_kernel_{self.K}x{self.K}",
            "contract": self.contract.to_dict(),
            "direct_latency_ms": direct_cost.wall_clock_ms,
            "separable_latency_ms": sep_cost.wall_clock_ms,
            "verified_speedup": round(speedup, 2),
            "verification_status": v_res.trust_level,
            "is_verified": v_res.is_valid,
            "relative_error": v_res.relative_error,
        }
