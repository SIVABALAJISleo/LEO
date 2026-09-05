"""
hyper_mvc_dar/ucsp/tier2_speculative_oracle.py
TIER 2: REDUCED-WORK SPECULATION (The "Oracle" Layer)
Speculative computation with Freivalds' Probabilistic Verification.
Reduces verification of A @ B = C_approx from O(N^3) to O(N^2).
Guarantees mathematical correctness bounds before passing output.
"""

import time
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger("UCSP.Tier2")


class FreivaldsVerifier:
    """
    Randomized Freivalds Probabilistic Verifier.
    Verifies if A @ B == C_approx in O(N^2) time via random vector probes.
    For k trials, probability of failing to detect an incorrect matrix product is <= 2^-k.
    """

    @staticmethod
    def verify(
        A: np.ndarray,
        B: np.ndarray,
        C_approx: np.ndarray,
        num_trials: int = 4,
        tolerance: float = 1e-3
    ) -> Tuple[bool, float, float]:
        """
        Evaluates Freivalds' certificate.
        Returns:
            (is_verified, max_error, latency_ms)
        """
        t_start = time.perf_counter()
        M, K = A.shape
        K2, N = B.shape
        if K != K2:
            raise ValueError(f"Inner dimension mismatch: {A.shape} vs {B.shape}")
        if C_approx.shape != (M, N):
            raise ValueError(f"Output shape mismatch: {C_approx.shape} vs expected {(M, N)}")

        max_discrepancy = 0.0

        for _ in range(num_trials):
            # Random vector r in {-1, +1}^N
            r = np.random.choice([-1.0, 1.0], size=(N, 1)).astype(A.dtype)

            # Br = B @ r -> O(K * N)
            Br = np.matmul(B, r)

            # ABr = A @ (B @ r) -> O(M * K)
            ABr = np.matmul(A, Br)

            # Cr = C_approx @ r -> O(M * N)
            Cr = np.matmul(C_approx, r)

            diff = np.max(np.abs(ABr - Cr))
            if diff > max_discrepancy:
                max_discrepancy = float(diff)

            if diff > tolerance:
                latency_ms = (time.perf_counter() - t_start) * 1000.0
                return False, max_discrepancy, latency_ms

        latency_ms = (time.perf_counter() - t_start) * 1000.0
        return True, max_discrepancy, latency_ms


class SpeculativeOracle:
    """
    Tier 2 Speculative Execution Engine.
    Executes a fast speculative approximation (e.g., low-rank SVD or quantized surrogate),
    probabilistically verifies it via Freivalds' Algorithm in O(N^2) time,
    and returns verified result or signals escalation to Tier 3.
    """

    def __init__(self, default_trials: int = 3, error_tolerance: float = 1e-2):
        self.default_trials = default_trials
        self.error_tolerance = error_tolerance
        self.verifier = FreivaldsVerifier()
        # Telemetry
        self.speculative_attempts = 0
        self.speculative_verified = 0
        self.speculative_rejected = 0

    def speculative_draft(self, A: np.ndarray, B: np.ndarray, rank_fraction: float = 0.25) -> np.ndarray:
        """
        Creates a fast low-rank draft approximation:
        A ~ U_k @ S_k, B ~ V_k -> C_draft = (U_k S_k) @ (V_k)
        Cost is O(N^2 * k) with k << N.
        """
        M, K = A.shape
        K2, N = B.shape
        target_k = max(2, int(min(M, K, N) * rank_fraction))

        # Fast randomized SVD or truncated projection
        # Subsampled columns of A and rows of B
        idx_k = np.linspace(0, K - 1, target_k, dtype=int)
        A_sub = A[:, idx_k]
        B_sub = B[idx_k, :]
        scale = K / float(target_k)
        C_draft = np.matmul(A_sub, B_sub) * scale
        return C_draft

    def execute_speculative(
        self,
        A: np.ndarray,
        B: np.ndarray,
        custom_draft: Optional[np.ndarray] = None,
        tolerance: Optional[float] = None
    ) -> Tuple[Optional[np.ndarray], str, float, bool]:
        """
        Attempts speculative execution and Freivalds verification.
        Returns:
            (result_matrix, status, latency_ms, is_verified)
        """
        t_start = time.perf_counter()
        self.speculative_attempts += 1
        tol = tolerance if tolerance is not None else self.error_tolerance

        # 1. Obtain or compute draft
        C_draft = custom_draft if custom_draft is not None else self.speculative_draft(A, B)

        # 2. Verify via Freivalds
        verified, max_err, verif_ms = self.verifier.verify(
            A, B, C_draft, num_trials=self.default_trials, tolerance=tol
        )

        total_ms = (time.perf_counter() - t_start) * 1000.0

        if verified:
            self.speculative_verified += 1
            return C_draft, "TIER_2_SPECULATION_VERIFIED", total_ms, True
        else:
            self.speculative_rejected += 1
            return None, "TIER_2_VERIFICATION_FAILED", total_ms, False
