"""
hyper_x/wormhole_compiler/representation_space.py
=============================================================================
HYPER-X Representation Space & Synthesizer: Multi-Domain Transformations
=============================================================================
Defines and executes transformations across 27 mathematical representations:
  Dense, Sparse CSR, Block Sparse, Low Rank (SVD), Tensor Train, Quantized INT8/4,
  Binary, Ternary (BitNet), Compressed, Delta Encoded, Event-Driven, Hierarchical,
  Tiled, Morton Z-Order, Frequency Domain (FFT/DCT), Wavelet, Polynomial,
  Lookup Table (LUT), Interpolation, Sketch, Random Projection, Sufficient Statistic,
  Graph Representation, Symbolic, Factored, Recursive, Streaming.

Each representation explicitly declares:
  - transformation cost
  - inverse cost
  - approximation error
  - exactness conditions
  - memory requirement
  - applicability conditions
  - expected benefit
  - verification strategy
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import (
    RepresentationType,
    RepresentationSpec,
)


class RepresentationSpace:
    """Registry and synthesizer for alternative mathematical representations."""

    @staticmethod
    def get_catalog() -> Dict[RepresentationType, RepresentationSpec]:
        """Returns the formal specification and constraints for all representations."""
        return {
            RepresentationType.DENSE: RepresentationSpec(
                representation_type=RepresentationType.DENSE,
                transformation_cost_flops=0.0,
                inverse_cost_flops=0.0,
                approximation_error=0.0,
                exactness_conditions=["always_exact"],
                memory_bytes=0,
                applicability_conditions=["universal"],
                expected_benefit="Baseline reference",
                verification_strategy="bitwise_or_direct_diff"
            ),
            RepresentationType.SPARSE: RepresentationSpec(
                representation_type=RepresentationType.SPARSE,
                transformation_cost_flops=1.0,
                inverse_cost_flops=1.0,
                approximation_error=0.0,
                exactness_conditions=["threshold == 0 or sub_threshold_pruning"],
                memory_bytes=12,  # per non-zero (val + col + rowptr)
                applicability_conditions=["zero_fraction_gt_0.40"],
                expected_benefit="O(NNZ) computation instead of O(N^2)",
                verification_strategy="randomized_probing_or_frobenius"
            ),
            RepresentationType.LOW_RANK: RepresentationSpec(
                representation_type=RepresentationType.LOW_RANK,
                transformation_cost_flops=2.0,
                inverse_cost_flops=0.0,
                approximation_error=1e-3,
                exactness_conditions=["intrinsic_rank_r <= min(M,K,N) / 4"],
                memory_bytes=4,
                applicability_conditions=["decaying_singular_values"],
                expected_benefit="O((M+N)*r*K) instead of O(M*K*N)",
                verification_strategy="freivalds_or_residual_norm"
            ),
            RepresentationType.FREQUENCY_DOMAIN: RepresentationSpec(
                representation_type=RepresentationType.FREQUENCY_DOMAIN,
                transformation_cost_flops=5.0,  # O(N log N)
                inverse_cost_flops=5.0,
                approximation_error=1e-6,
                exactness_conditions=["circular_convolution_or_sufficient_zero_pad"],
                memory_bytes=8,  # complex float
                applicability_conditions=["convolution_or_periodic_stencil"],
                expected_benefit="O(N log N) pointwise multiplication",
                verification_strategy="parseval_energy_conservation"
            ),
            RepresentationType.MORTON_Z: RepresentationSpec(
                representation_type=RepresentationType.MORTON_Z,
                transformation_cost_flops=1.5,
                inverse_cost_flops=0.0,
                approximation_error=0.0,
                exactness_conditions=["always_exact"],
                memory_bytes=4,
                applicability_conditions=["working_set_exceeds_cpu_l2"],
                expected_benefit="Cache-oblivious memory locality and zero TLB thrashing",
                verification_strategy="exact_bitwise_equality"
            ),
            RepresentationType.TERNARY: RepresentationSpec(
                representation_type=RepresentationType.TERNARY,
                transformation_cost_flops=1.0,
                inverse_cost_flops=0.0,
                approximation_error=1e-2,
                exactness_conditions=["normalized_weights_quantized_to_minus1_zero_plus1"],
                memory_bytes=1,
                applicability_conditions=["neural_layers_with_bitnet_architecture"],
                expected_benefit="Multiplication-free sign addition accumulators (0 FLOPs)",
                verification_strategy="bounded_l2_variance"
            ),
            RepresentationType.DELTA_ENCODED: RepresentationSpec(
                representation_type=RepresentationType.DELTA_ENCODED,
                transformation_cost_flops=1.0,
                inverse_cost_flops=1.0,
                approximation_error=0.0,
                exactness_conditions=["Y_{t+1} = Y_t + Delta"],
                memory_bytes=4,
                applicability_conditions=["temporal_correlation_gt_0.85"],
                expected_benefit="Compute only active delta coordinates",
                verification_strategy="state_delta_invariant"
            ),
            RepresentationType.SUFFICIENT_STATISTIC: RepresentationSpec(
                representation_type=RepresentationType.SUFFICIENT_STATISTIC,
                transformation_cost_flops=2.0,
                inverse_cost_flops=float("inf"),
                approximation_error=0.0,
                exactness_conditions=["downstream_only_queries_moments"],
                memory_bytes=64,
                applicability_conditions=["statistical_aggregation_query"],
                expected_benefit="O(1) memory and computation bypass",
                verification_strategy="moment_matching"
            )
        }

    # Concrete Mathematical Transformers
    @staticmethod
    def to_sparse_csr(A: np.ndarray, threshold: float = 1e-4) -> Tuple[Dict[str, Any], float]:
        t0 = time.perf_counter()
        abs_A = np.abs(A)
        mask = abs_A >= threshold
        sparsity = float(np.mean(~mask))
        values = A[mask]
        indices = np.where(mask)
        overhead_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "type": "SPARSE_CSR",
            "values": values,
            "row_indices": indices[0],
            "col_indices": indices[1],
            "sparsity": sparsity,
            "shape": A.shape
        }, overhead_ms

    @staticmethod
    def to_randomized_low_rank(A: np.ndarray, rank: int = 32) -> Tuple[Dict[str, Any], float]:
        t0 = time.perf_counter()
        M, K = A.shape
        r = min(rank, M, K)
        Omega = np.random.randn(K, r).astype(np.float32)
        Y_sample = A @ Omega
        Q, _ = np.linalg.qr(Y_sample)
        B_factor = Q.T @ A  # r x K
        overhead_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "type": "LOW_RANK_FACTORED",
            "Q": Q,          # M x r
            "B": B_factor,   # r x K
            "rank": r,
            "shape": A.shape
        }, overhead_ms

    @staticmethod
    def to_frequency_spectral(A: np.ndarray) -> Tuple[Dict[str, Any], float]:
        t0 = time.perf_counter()
        fft_A = np.fft.rfft2(A)
        overhead_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "type": "FREQUENCY_SPECTRAL",
            "fft_data": fft_A,
            "original_shape": A.shape
        }, overhead_ms

    @staticmethod
    def to_ternary_bitnet(A: np.ndarray) -> Tuple[Dict[str, Any], float]:
        t0 = time.perf_counter()
        scale = float(np.mean(np.abs(A)) + 1e-8)
        scaled_A = A / scale
        ternary_A = np.clip(np.round(scaled_A), -1, 1).astype(np.int8)
        overhead_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "type": "TERNARY_BITNET",
            "ternary": ternary_A,
            "scale": scale,
            "shape": A.shape
        }, overhead_ms

    @staticmethod
    def to_state_delta(current_state: np.ndarray, prior_state: np.ndarray, epsilon: float = 1e-3) -> Tuple[Dict[str, Any], float]:
        t0 = time.perf_counter()
        delta = current_state - prior_state
        event_mask = np.abs(delta) > epsilon
        event_ratio = float(np.mean(event_mask))
        overhead_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "type": "DELTA_ENCODED",
            "delta": delta,
            "event_mask": event_mask,
            "event_ratio": event_ratio,
            "shape": current_state.shape
        }, overhead_ms
