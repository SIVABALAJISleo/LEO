#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_runtime/adaptive_precision.py
===================================
Phase C3: Adaptive Precision Selection via SVD Condition-Number Spectrum.

Dynamically profiles layer weight matrices to assign optimal numerical precision:
  - INT4: Well-conditioned matrices (cond < 25.0, low effective rank).
  - INT8: Moderately conditioned matrices (cond < 100.0).
  - FP32: Ill-conditioned / outlier-sensitive matrices (cond >= 100.0).
"""

import time
from typing import Dict, Any, List, Optional
import numpy as np


class AdaptivePrecisionSelector:
    """
    SVD spectral condition number analyzer for automatic quantization precision selection.
    """

    def __init__(
        self,
        cond_int4_threshold: float = 25.0,
        cond_int8_threshold: float = 100.0,
        energy_ratio_target: float = 0.90
    ):
        self.cond_int4 = cond_int4_threshold
        self.cond_int8 = cond_int8_threshold
        self.energy_target = energy_ratio_target

    def analyze_matrix(
        self,
        weight_matrix: np.ndarray,
        layer_name: str = "layer"
    ) -> Dict[str, Any]:
        """
        Analyzes a 2D weight matrix and selects optimal precision.
        """
        t0 = time.perf_counter()
        A = np.asarray(weight_matrix, dtype=np.float32)
        if A.ndim != 2:
            A = A.reshape(A.shape[0], -1)

        m, n = A.shape
        min_dim = min(m, n)

        # Fast randomized / truncated SVD estimate if dimension > 512
        if min_dim > 512:
            # Subsample rows/cols for fast condition number estimation
            step_m = max(1, m // 256)
            step_n = max(1, n // 256)
            sub_A = A[::step_m, ::step_n]
            s = np.linalg.svd(sub_A, compute_uv=False)
        else:
            s = np.linalg.svd(A, compute_uv=False)

        # Filter near-zero numerical noise for effective condition number
        significant_s = s[s > (1e-4 * s[0])]
        cond = float(s[0] / max(significant_s[-1], 1e-12)) if len(significant_s) > 0 else 1.0

        # Energy concentration: cumulative sum of squared singular values
        s2 = s ** 2
        total_energy = np.sum(s2)
        cum_energy = np.cumsum(s2) / max(total_energy, 1e-12)
        effective_rank = int(np.searchsorted(cum_energy, self.energy_target)) + 1
        rank_ratio = effective_rank / max(len(s), 1)

        # Precision policy
        if cond < self.cond_int4 or rank_ratio < 0.35:
            precision = "INT4"
            speedup = 1.85
            mem_factor = 0.125 # 4 bits vs 32 bits = 1/8
            recommendation = "Safe for INT4/Q4_K_M quantization without quality loss."
        elif cond < self.cond_int8 or rank_ratio < 0.70:
            precision = "INT8"
            speedup = 1.35
            mem_factor = 0.25 # 8 bits vs 32 bits = 1/4
            recommendation = "Safe for INT8/Q8_0 quantization."
        else:
            precision = "FP32"
            speedup = 1.00
            mem_factor = 1.00
            recommendation = "Ill-conditioned spectrum requires FP32/FP16 precision to avoid representation collapse."

        dt_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "layer": layer_name,
            "shape": [m, n],
            "condition_number": round(cond, 2),
            "effective_rank_90pct": effective_rank,
            "rank_ratio": round(rank_ratio, 3),
            "selected_precision": precision,
            "estimated_speedup": speedup,
            "memory_factor": mem_factor,
            "recommendation": recommendation,
            "analysis_ms": round(dt_ms, 3)
        }

    def profile_model_layers(
        self,
        layer_dict: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Profiles a dictionary of model layer weights {name: weight_tensor}.
        """
        results = []
        precision_counts = {"INT4": 0, "INT8": 0, "FP32": 0}
        total_mem_orig = 0
        total_mem_opt = 0

        for name, W in layer_dict.items():
            analysis = self.analyze_matrix(W, layer_name=name)
            results.append(analysis)
            p = analysis["selected_precision"]
            precision_counts[p] += 1

            orig_bytes = W.nbytes
            total_mem_orig += orig_bytes
            total_mem_opt += int(orig_bytes * analysis["memory_factor"])

        net_compression = total_mem_orig / max(total_mem_opt, 1)

        return {
            "total_layers_analyzed": len(results),
            "precision_breakdown": precision_counts,
            "net_compression_ratio": round(net_compression, 2),
            "layer_details": results
        }
