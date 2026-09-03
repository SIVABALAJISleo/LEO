"""
hyper_v3/workloads/adversarial_suite.py
Adversarial workloads designed to defeat caching, low-rank factorization, and naive heuristics.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack


class AdversarialSuite:
    """Stress tests for extreme condition numbers, zero-sparsity dense randoms, and prediction-hostile signals."""

    @staticmethod
    def run_adv_ill_conditioned_gemm(contract: ExecutionContract) -> Tuple[np.ndarray, float, int, int]:
        n = 512
        ref_flops = 2 * n * n * n
        np.random.seed(999)
        u, _ = np.linalg.qr(np.random.randn(n, n))
        s = np.diag(np.logspace(0, -8, n))
        a = (u @ s @ u.T).astype(np.float32)
        b = np.random.randn(n, n).astype(np.float32)

        t0 = time.perf_counter()
        c = np.matmul(a, b)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return c, elapsed_us, ref_flops, ref_flops

    @staticmethod
    def run_adv_high_entropy_signal_fft(contract: ExecutionContract) -> Tuple[np.ndarray, float, int, int]:
        n = 8192
        ref_flops = int(5 * n * np.log2(n))
        np.random.seed(998)
        white_noise = np.random.randn(n).astype(np.float32)

        t0 = time.perf_counter()
        spectrum = np.fft.fft(white_noise)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return spectrum, elapsed_us, ref_flops, ref_flops

    @staticmethod
    def run_adv_zero_reuse_stream(contract: ExecutionContract) -> Tuple[np.ndarray, float, int, int]:
        n = 1000
        ref_flops = n * 512 * 2
        np.random.seed(int(time.time() * 1000) % 100000)
        query = np.random.randn(1, 512).astype(np.float32)
        db = np.random.randn(n, 512).astype(np.float32)

        t0 = time.perf_counter()
        sims = np.dot(query, db.T)[0]
        top10 = np.argsort(sims)[::-1][:10]
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return top10.astype(np.float32), elapsed_us, ref_flops, ref_flops
