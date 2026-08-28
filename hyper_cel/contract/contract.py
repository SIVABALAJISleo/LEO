"""
hyper_cel/contract/contract.py
=============================================================================
HYPER-CEL: Computational Contract Definitions
=============================================================================
Formalizes the four fundamental contract classes:
  1. ExactContract: 0-error required (cryptography, hashing, exact mathematical logic)
  2. NumericContract: Bounded numerical error ||Y - Y_hat|| <= epsilon (scientific compute, FP32/FP16 approximations)
  3. PerceptualContract: Bounded perceptual quality SSIM >= tau, LPIPS <= gamma (graphics, rendering, vision)
  4. DistributionalContract: Bounded KL divergence / Perplexity match (LLM generation, sampling)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import numpy as np

class ComputationalContract(ABC):
    """Abstract base class for all computational quality contracts."""
    
    @abstractmethod
    def validate(self, candidate_output: Any, ground_truth_or_reference: Any) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Validates candidate output against contract bounds.
        Returns: (is_valid, quality_score, metrics_dict)
        """
        pass

class ExactContract(ComputationalContract):
    """Exact contract: Requires bitwise or exact value equivalence (0 tolerance)."""
    
    def validate(self, candidate: Any, reference: Any) -> Tuple[bool, float, Dict[str, Any]]:
        if isinstance(candidate, np.ndarray) and isinstance(reference, np.ndarray):
            match = bool(np.array_equal(candidate, reference))
        else:
            match = bool(candidate == reference)
        return match, 1.0 if match else 0.0, {"contract_type": "EXACT", "exact_match": match}

class NumericContract(ComputationalContract):
    """Numeric contract: Requires relative Frobenius or max absolute error <= epsilon."""
    
    def __init__(self, epsilon: float = 1e-3, norm_type: str = "frobenius"):
        self.epsilon = epsilon
        self.norm_type = norm_type

    def validate(self, candidate: np.ndarray, reference: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        if self.norm_type == "frobenius":
            ref_norm = float(np.linalg.norm(reference) + 1e-8)
            diff_norm = float(np.linalg.norm(reference - candidate))
            rel_error = diff_norm / ref_norm
            passed = rel_error <= self.epsilon
            quality = max(0.0, 1.0 - rel_error)
            return passed, quality, {"contract_type": "NUMERIC", "rel_error": rel_error, "epsilon": self.epsilon}
        else: # max absolute error
            max_err = float(np.max(np.abs(reference - candidate)))
            passed = max_err <= self.epsilon
            quality = max(0.0, 1.0 - (max_err / (float(np.max(np.abs(reference))) + 1e-8)))
            return passed, quality, {"contract_type": "NUMERIC", "max_err": max_err, "epsilon": self.epsilon}

class PerceptualContract(ComputationalContract):
    """Perceptual contract: Requires SSIM >= min_ssim and PSNR >= min_psnr for graphics/images."""
    
    def __init__(self, min_ssim: float = 0.95, min_psnr: float = 30.0, data_range: float = 1.0):
        self.min_ssim = min_ssim
        self.min_psnr = min_psnr
        self.data_range = data_range

    def validate(self, candidate: np.ndarray, reference: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        # Compute exact MSE & PSNR
        mse = float(np.mean((reference - candidate) ** 2))
        max_val = self.data_range
        psnr = float(20.0 * np.log10(max_val / np.sqrt(max(1e-10, mse))))

        # Structural similarity index metric (SSIM) approximation
        mu_x = float(np.mean(reference))
        mu_y = float(np.mean(candidate))
        sigma_x = float(np.var(reference))
        sigma_y = float(np.var(candidate))
        sigma_xy = float(np.mean((reference - mu_x) * (candidate - mu_y)))
        
        c1 = (0.01 * max_val) ** 2
        c2 = (0.03 * max_val) ** 2
        ssim = float(((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / ((mu_x**2 + mu_y**2 + c1) * (sigma_x + sigma_y + c2)))

        passed = (ssim >= self.min_ssim) and (psnr >= self.min_psnr)
        return passed, ssim, {"contract_type": "PERCEPTUAL", "ssim": ssim, "psnr": psnr, "mse": mse}
