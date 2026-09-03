"""
hyper_v3/verification/perceptual.py
Perceptual SSIM and visual fidelity validation for graphics and video workloads.
"""

import numpy as np
from hyper_v3.verification.independent_verifier import IndependentVerifier


class PerceptualVerifier:
    @staticmethod
    def verify_ssim(reference_frame: np.ndarray, candidate_frame: np.ndarray, min_ssim: float = 0.95) -> bool:
        score = IndependentVerifier.compute_ssim_2d(reference_frame, candidate_frame)
        return bool(score >= min_ssim)
