"""
hyper_v3/workloads/holdout_suite.py
Frozen blind holdout suite with unseen non-standard matrix shapes and signal dimensions.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack


class HoldoutSuite:
    """Frozen holdout workloads with non-power-of-two dimensions and adversarial noise."""

    @staticmethod
    def run_holdout_odd_gemm(contract: ExecutionContract) -> Tuple[np.ndarray, float, int, int]:
        m, n, k = 733, 519, 641  # Prime/odd dimensions
        ref_flops = 2 * m * n * k
        np.random.seed(777)
        a = np.random.randn(m, k).astype(np.float32)
        b = np.random.randn(k, n).astype(np.float32)

        t0 = time.perf_counter()
        c = np.matmul(a, b)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return c, elapsed_us, ref_flops, ref_flops

    @staticmethod
    def run_holdout_multiscale_signal_fft(contract: ExecutionContract) -> Tuple[np.ndarray, float, int, int]:
        n = 11111  # Non-power-of-two
        ref_flops = int(5 * n * np.log2(n))
        np.random.seed(888)
        sig = np.random.randn(n).astype(np.float32)

        t0 = time.perf_counter()
        res = np.fft.fft(sig)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return res, elapsed_us, ref_flops, ref_flops
