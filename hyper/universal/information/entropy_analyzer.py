"""
hyper/universal/information/entropy_analyzer.py
===============================================
Analyzes information content, Shannon entropy, algorithmic compressibility
(Kolmogorov proxy), and sparsity structure of workload inputs.
"""

from __future__ import annotations

import math
import zlib
from typing import Any, Dict, Optional, Tuple
import numpy as np


class EntropyAnalyzer:
    """Estimates information entropy and compressibility of computational inputs."""

    @staticmethod
    def analyze_entropy(data: Any) -> Dict[str, Any]:
        if not isinstance(data, np.ndarray):
            # General object entropy estimation
            raw_bytes = str(data).encode("utf-8")
            comp_bytes = zlib.compress(raw_bytes)
            ratio = len(comp_bytes) / max(1, len(raw_bytes))
            return {
                "is_array": False,
                "sparsity_ratio": 0.0,
                "shannon_entropy_bits": 8.0 * ratio,
                "compression_ratio": ratio,
                "is_compressible": ratio < 0.8,
                "is_sparse": False,
            }

        # For NumPy arrays
        total_elements = data.size
        if total_elements == 0:
            return {
                "is_array": True,
                "sparsity_ratio": 1.0,
                "shannon_entropy_bits": 0.0,
                "compression_ratio": 0.0,
                "is_compressible": True,
                "is_sparse": True,
            }

        # Sparsity
        zero_count = int(np.count_nonzero(data == 0))
        sparsity = zero_count / total_elements

        # Shannon entropy over quantized values or byte representation
        raw_bytes = data.tobytes()
        comp_bytes = zlib.compress(raw_bytes)
        compression_ratio = len(comp_bytes) / max(1, len(raw_bytes))

        # Sample for empirical Shannon entropy
        sample = data.ravel()[: min(total_elements, 10000)]
        _, counts = np.unique(sample, return_counts=True)
        probs = counts / counts.sum()
        shannon = float(-np.sum(probs * np.log2(probs + 1e-12)))

        return {
            "is_array": True,
            "total_elements": total_elements,
            "zero_count": zero_count,
            "sparsity_ratio": round(sparsity, 4),
            "shannon_entropy_bits": round(shannon, 4),
            "compression_ratio": round(compression_ratio, 4),
            "is_compressible": compression_ratio < 0.75,
            "is_sparse": sparsity > 0.4,
            "is_ultra_sparse": sparsity > 0.85,
        }
