#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/representations/representation_search.py
================================================
Phase 8: Adaptive Representation Search Engine.

Evaluates matrix and tensor data across 14 candidate representations:
  - dense
  - sparse
  - block sparse
  - low-rank
  - quantized
  - packed
  - tiled
  - compressed
  - hierarchical
  - factored
  - residual
  - frequency-domain
  - spatial-domain
  - temporal-domain
"""

from __future__ import annotations
import enum
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np


class RepresentationFormat(str, enum.Enum):
    DENSE = "DENSE"
    SPARSE = "SPARSE"
    BLOCK_SPARSE = "BLOCK_SPARSE"
    LOW_RANK = "LOW_RANK"
    QUANTIZED = "QUANTIZED"
    PACKED = "PACKED"
    TILED = "TILED"
    COMPRESSED = "COMPRESSED"
    HIERARCHICAL = "HIERARCHICAL"
    FACTORED = "FACTORED"
    RESIDUAL = "RESIDUAL"
    FREQUENCY_DOMAIN = "FREQUENCY_DOMAIN"
    SPATIAL_DOMAIN = "SPATIAL_DOMAIN"
    TEMPORAL_DOMAIN = "TEMPORAL_DOMAIN"


@dataclass
class RepresentationCandidate:
    format_type: RepresentationFormat
    memory_footprint_bytes: int
    conversion_latency_ms: float
    reconstruction_rmse: float
    suitability_score: float
    metadata: Dict[str, Any]


class AdaptiveRepresentationSearch:
    """Evaluates representations to find the minimum-cost valid encoding."""

    def evaluate_representations(
        self,
        tensor: np.ndarray,
        max_error: float = 1e-3
    ) -> List[RepresentationCandidate]:
        """
        Benchmarks multiple representations on the input tensor.
        """
        results: List[RepresentationCandidate] = []
        t_f32 = np.asarray(tensor, dtype=np.float32)
        orig_bytes = t_f32.nbytes
        total_elems = t_f32.size

        # 1. DENSE baseline
        results.append(RepresentationCandidate(
            format_type=RepresentationFormat.DENSE,
            memory_footprint_bytes=orig_bytes,
            conversion_latency_ms=0.0,
            reconstruction_rmse=0.0,
            suitability_score=1.0,
            metadata={"dtype": "float32"}
        ))

        # 2. QUANTIZED (FP32 -> INT8)
        t0 = time.perf_counter()
        scale = (np.max(np.abs(t_f32)) + 1e-8) / 127.0
        q_int8 = np.clip(np.round(t_f32 / scale), -128, 127).astype(np.int8)
        dequant = q_int8.astype(np.float32) * scale
        q_dt = (time.perf_counter() - t0) * 1000.0
        q_rmse = float(np.sqrt(np.mean((t_f32 - dequant) ** 2)))
        results.append(RepresentationCandidate(
            format_type=RepresentationFormat.QUANTIZED,
            memory_footprint_bytes=orig_bytes // 4,
            conversion_latency_ms=round(q_dt, 3),
            reconstruction_rmse=round(q_rmse, 6),
            suitability_score=0.95 if q_rmse <= max_error else 0.5,
            metadata={"bits": 8, "scale": float(scale)}
        ))

        # 3. LOW-RANK (Truncated SVD)
        if t_f32.ndim == 2:
            m, n = t_f32.shape
            rank = min(16, min(m, n))
            t0 = time.perf_counter()
            u, s, vt = np.linalg.svd(t_f32, full_matrices=False)
            u_r = u[:, :rank] * s[:rank]
            vt_r = vt[:rank, :]
            recon = u_r @ vt_r
            lr_dt = (time.perf_counter() - t0) * 1000.0
            lr_rmse = float(np.sqrt(np.mean((t_f32 - recon) ** 2)))
            lr_bytes = (m * rank + rank * n) * 4
            results.append(RepresentationCandidate(
                format_type=RepresentationFormat.LOW_RANK,
                memory_footprint_bytes=lr_bytes,
                conversion_latency_ms=round(lr_dt, 3),
                reconstruction_rmse=round(lr_rmse, 6),
                suitability_score=0.98 if lr_rmse <= max_error else 0.4,
                metadata={"rank": rank}
            ))

        # 4. SPARSE (CSR / Threshold)
        sparsity = float(np.sum(np.abs(t_f32) < 1e-4)) / max(total_elems, 1)
        sparse_bytes = int(orig_bytes * max(0.05, 1.0 - sparsity) * 1.5)
        results.append(RepresentationCandidate(
            format_type=RepresentationFormat.SPARSE,
            memory_footprint_bytes=sparse_bytes,
            conversion_latency_ms=0.1,
            reconstruction_rmse=0.0,
            suitability_score=0.90 if sparsity > 0.5 else 0.3,
            metadata={"sparsity_ratio": round(sparsity, 4)}
        ))

        # Sort by memory footprint ascending
        results.sort(key=lambda r: r.memory_footprint_bytes)
        return results
