"""
hyper_v2/verification/independent_verifier.py
Segregated, independent verification engine for validating mathematical contracts.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class VerificationOutcome:
    workload_id: str
    is_verified: bool
    metric_name: str
    measured_value: float
    contract_bound: float
    margin: float
    verification_mode: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "status": "PASS" if self.is_verified else "FAIL",
            "metric_name": self.metric_name,
            "measured_value": float(self.measured_value),
            "contract_bound": float(self.contract_bound),
            "margin": float(self.margin),
            "verification_mode": self.verification_mode
        }


class IndependentVerifier:
    """Provides isolated, mathematically sound verification algorithms."""

    @staticmethod
    def verify_freivalds_matmul(A: np.ndarray, B: np.ndarray, C_approx: np.ndarray, epsilon: float = 1e-3, k_trials: int = 5) -> VerificationOutcome:
        """Freivalds algorithm: tests ||A*(B*r) - C*r|| <= eps*||A*(B*r)|| for random r in {0,1}^N in O(k*N^2)."""
        N = B.shape[1]
        passed = True
        max_rel_error = 0.0

        for _ in range(k_trials):
            r = np.random.randint(0, 2, size=(N, 1)).astype(A.dtype)
            # Brute force (A*B)*r is O(N^3), but A*(B*r) is O(N^2)
            Br = np.dot(B, r)
            ABr = np.dot(A, Br)
            Cr = np.dot(C_approx, r)

            diff_norm = np.linalg.norm(ABr - Cr)
            ref_norm = np.linalg.norm(ABr) + 1e-12
            rel_err = float(diff_norm / ref_norm)
            max_rel_error = max(max_rel_error, rel_err)

            if rel_err > epsilon:
                passed = False
                break

        return VerificationOutcome(
            workload_id="gemm_freivalds",
            is_verified=passed,
            metric_name="Relative L2 Norm Error",
            measured_value=max_rel_error,
            contract_bound=epsilon,
            margin=epsilon - max_rel_error,
            verification_mode="FREIVALDS_O(N^2)_PROBABILISTIC"
        )

    @staticmethod
    def verify_ssim(image_true: np.ndarray, image_test: np.ndarray, min_ssim: float = 0.95) -> VerificationOutcome:
        """Computes structural similarity index (SSIM) between reference and reconstructed image."""
        # Mean, variance, covariance on normalized [0, 1] arrays
        I1 = np.clip(image_true.astype(np.float32) / 255.0 if image_true.max() > 1.0 else image_true, 0, 1)
        I2 = np.clip(image_test.astype(np.float32) / 255.0 if image_test.max() > 1.0 else image_test, 0, 1)

        mu1 = float(np.mean(I1))
        mu2 = float(np.mean(I2))
        sigma1_sq = float(np.var(I1))
        sigma2_sq = float(np.var(I2))
        sigma12 = float(np.mean((I1 - mu1) * (I2 - mu2)))

        c1 = 0.01 ** 2
        c2 = 0.03 ** 2
        ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / ((mu1**2 + mu2**2 + c1) * (sigma1_sq + sigma2_sq + c2))
        ssim = float(np.clip(ssim, 0.0, 1.0))

        return VerificationOutcome(
            workload_id="image_perceptual_ssim",
            is_verified=ssim >= min_ssim,
            metric_name="SSIM (Structural Similarity)",
            measured_value=ssim,
            contract_bound=min_ssim,
            margin=ssim - min_ssim,
            verification_mode="DETERMINISTIC_PERCEPTUAL_SSIM"
        )

    @staticmethod
    def verify_nbody_symplectic_drift(energy_init: float, energy_final: float, max_drift_ratio: float = 1e-3) -> VerificationOutcome:
        """Verifies total Hamiltonian mechanical energy conservation."""
        drift = abs(energy_final - energy_init) / max(1e-12, abs(energy_init))
        return VerificationOutcome(
            workload_id="nbody_symplectic_energy",
            is_verified=drift <= max_drift_ratio,
            metric_name="Hamiltonian Energy Drift Ratio",
            measured_value=drift,
            contract_bound=max_drift_ratio,
            margin=max_drift_ratio - drift,
            verification_mode="SYMPLECTIC_CONSERVATION_CHECK"
        )
