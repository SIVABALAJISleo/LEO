"""
hyper_mvc_dar/representations.py
Representation Discovery Engine: Evaluates data representations (dense, sparse, quantized,
ternary BitNet {-1, 0, +1}, and frequency-domain) to minimize execution cost.
"""

from enum import Enum, auto
from typing import Dict, Any, Tuple
import numpy as np


class RepresentationType(Enum):
    DENSE_FP32 = "DENSE_FP32"
    STRUCTURED_SPARSE_2_4 = "STRUCTURED_SPARSE_2_4"
    TERNARY_BITNET = "TERNARY_BITNET_1_58"
    LOW_RANK_FACTORED = "LOW_RANK_FACTORED"
    FREQUENCY_FOURIER = "FREQUENCY_FOURIER"
    HASHED_SKETCH = "HASHED_SKETCH"


class RepresentationDiscoveryEngine:
    """Selects optimal tensor storage and arithmetic representation based on contract."""

    @staticmethod
    def recommend_representation(tensor: np.ndarray, error_tolerance: float) -> RepresentationType:
        # Check for zero sparsity
        zero_ratio = float(np.sum(tensor == 0)) / tensor.size
        if zero_ratio >= 0.75:
            return RepresentationType.STRUCTURED_SPARSE_2_4

        # Check for ternary distribution {-1, 0, +1}
        unique_vals = np.unique(np.round(tensor))
        if len(unique_vals) <= 3 and set(unique_vals).issubset({-1.0, 0.0, 1.0}):
            return RepresentationType.TERNARY_BITNET

        # Check for low-rank SVD compressability if error is tolerated
        if error_tolerance >= 0.01 and len(tensor.shape) == 2:
            m, n = tensor.shape
            if min(m, n) >= 256:
                return RepresentationType.LOW_RANK_FACTORED

        return RepresentationType.DENSE_FP32
