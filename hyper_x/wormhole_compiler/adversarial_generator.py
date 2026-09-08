"""
hyper_x/wormhole_compiler/adversarial_generator.py
=============================================================================
HYPER-X Adversarial Input & Pathological Stress Generator (Phase 13)
=============================================================================
Synthesizes adversarial test cases designed to attack and falsify candidate
algorithms:
  1. Dense Gaussian (High Entropy, Full Rank)
  2. Sparse Bernoulli / Power Law
  3. Ill-Conditioned Exponential Decay (Condition Number > 10^6)
  4. Pathological Coordinate Spikes & Outliers
  5. Extreme Aspect Ratios (Tall-Skinny 1x1024, Wide-Short 1024x1)
  6. Rank-Deficient Near-Singular Matrices
  7. Distribution Shifts & Non-Stationary Perturbations
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np


class AdversarialGenerator:
    """Generates rigorous stress matrices to attack and falsify candidates."""

    @staticmethod
    def dense_gaussian(shape: Tuple[int, int], seed: int = 101) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.standard_normal(shape).astype(np.float32)

    @staticmethod
    def sparse_bernoulli(shape: Tuple[int, int], sparsity: float = 0.90, seed: int = 102) -> np.ndarray:
        rng = np.random.default_rng(seed)
        mask = rng.uniform(0.0, 1.0, shape) > sparsity
        vals = rng.standard_normal(shape).astype(np.float32)
        return (vals * mask).astype(np.float32)

    @staticmethod
    def ill_conditioned_exponential(dim: int, condition_number: float = 1e6, seed: int = 103) -> np.ndarray:
        """Constructs matrix with singular values exponentially decaying to cond."""
        rng = np.random.default_rng(seed)
        U, _ = np.linalg.qr(rng.standard_normal((dim, dim)))
        V, _ = np.linalg.qr(rng.standard_normal((dim, dim)))
        s = np.logspace(0, -np.log10(max(1e1, condition_number)), dim).astype(np.float32)
        return ((U * s) @ V).astype(np.float32)

    @staticmethod
    def pathological_spikes(shape: Tuple[int, int], spike_factor: float = 1e4, seed: int = 104) -> np.ndarray:
        """Matrix with localized extreme magnitude outliers."""
        rng = np.random.default_rng(seed)
        mat = rng.standard_normal(shape).astype(np.float32) * 0.01
        M, K = shape
        mat[0, 0] = spike_factor
        mat[M - 1, K - 1] = -spike_factor
        mat[M // 2, K // 2] = spike_factor * 0.5
        return mat

    @staticmethod
    def extreme_aspect_ratio(dim: int = 128, seed: int = 105) -> Tuple[np.ndarray, np.ndarray]:
        """Tall-skinny @ wide-short vector dot product."""
        rng = np.random.default_rng(seed)
        A = rng.standard_normal((1, dim)).astype(np.float32)
        B = rng.standard_normal((dim, 1)).astype(np.float32)
        return A, B

    @staticmethod
    def low_rank_perturbed(shape: Tuple[int, int], rank: int = 4, noise_std: float = 1e-4, seed: int = 106) -> np.ndarray:
        rng = np.random.default_rng(seed)
        M, K = shape
        U = rng.standard_normal((M, rank)).astype(np.float32)
        V = rng.standard_normal((rank, K)).astype(np.float32)
        noise = rng.standard_normal((M, K)).astype(np.float32) * noise_std
        return (U @ V + noise).astype(np.float32)

    @classmethod
    def generate_battery(cls, dim: int = 64) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Generates full suite of 8 adversarial stress pairs."""
        return {
            "dense_gaussian": (cls.dense_gaussian((dim, dim), 1), cls.dense_gaussian((dim, dim), 2)),
            "sparse_bernoulli_90": (cls.sparse_bernoulli((dim, dim), 0.90, 3), cls.dense_gaussian((dim, dim), 4)),
            "ill_conditioned_1e6": (cls.ill_conditioned_exponential(dim, 1e6, 5), cls.dense_gaussian((dim, dim), 6)),
            "ill_conditioned_1e7": (cls.ill_conditioned_exponential(dim, 1e7, 7), cls.dense_gaussian((dim, dim), 8)),
            "pathological_spikes": (cls.pathological_spikes((dim, dim), 1e4, 9), cls.dense_gaussian((dim, dim), 10)),
            "low_rank_rank4": (cls.low_rank_perturbed((dim, dim), rank=4, noise_std=1e-4, seed=11), cls.dense_gaussian((dim, dim), 12)),
            "near_zero_matrix": (np.zeros((dim, dim), dtype=np.float32), cls.dense_gaussian((dim, dim), 13)),
            "identity_scaling": (np.eye(dim, dtype=np.float32) * 1e-2, cls.dense_gaussian((dim, dim), 14)),
        }
