"""
hyper_v3/verification/statistical.py
Statistical verification for Monte Carlo and stochastic sampling convergence.
"""

import numpy as np


class StatisticalVerifier:
    @staticmethod
    def verify_confidence_interval(samples: np.ndarray, expected_mean: float, confidence_level: float = 0.99) -> bool:
        n = samples.size
        if n < 2:
            return True
        mean = np.mean(samples)
        std_err = np.std(samples) / np.sqrt(n)
        z_val = 2.576 if confidence_level >= 0.99 else 1.96
        ci_lower = mean - z_val * std_err
        ci_upper = mean + z_val * std_err
        return bool(ci_lower <= expected_mean <= ci_upper)
